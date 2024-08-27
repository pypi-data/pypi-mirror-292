from fastapi import FastAPI, HTTPException, Query, APIRouter
from fastapi.responses import StreamingResponse, Response, JSONResponse, FileResponse
from urllib.parse import quote
from fastapi.staticfiles import StaticFiles

import functions_framework
from flask import jsonify, Request, Response, stream_with_context
from pydantic import BaseModel, Field
import io
import os
import json
import asyncio
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from botrun_ask_folder.constants import TOPIC_USER_INPUT_FOLDER
from botrun_ask_folder.embeddings_to_qdrant import embeddings_to_qdrant_distributed

from botrun_ask_folder.fast_api.util.pdf_util import pdf_page_to_image, DEFAULT_DPI
from botrun_ask_folder.google_drive_service import get_google_drive_service
from botrun_ask_folder.models.drive_file import DriveFile, DriveFileStatus
from botrun_ask_folder.models.drive_folder import DriveFolder, DriveFolderStatus
from botrun_ask_folder.models.splitted_file import SplittedFile, SplittedFileStatus
from botrun_ask_folder.run_split_txts import run_split_txts_for_distributed

from botrun_ask_folder.drive_download import (
    file_download_with_service,
)
from botrun_ask_folder.services.drive.drive_factory import (
    drive_client_factory,
)
from botrun_ask_folder.services.queue.queue_factory import (
    queue_client_factory,
)
from botrun_ask_folder.models.job_event import JobEvent
from botrun_ask_folder.workers.worker_pool import worker_pool

router = APIRouter(prefix="/botrun_ask_folder", tags=["botrun_ask_folder"])

# Mount static files
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
router.mount("/static", StaticFiles(directory=static_dir), name="static")


@router.get("/stress", response_class=FileResponse)
async def stress_page():
    return FileResponse(os.path.join(static_dir, "stress.html"))


@router.get("/download_file/{file_id}")
def download_file(file_id: str):
    service_account_file = "keys/google_service_account_key.json"
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build("drive", "v3", credentials=credentials)

    try:
        file = (
            drive_service.files().get(fileId=file_id, fields="name, mimeType").execute()
        )
        file_name = file.get("name")
        file_mime_type = file.get("mimeType")

        request = drive_service.files().get_media(fileId=file_id)

        def file_stream():
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                yield fh.getvalue()
                fh.seek(0)
                fh.truncate(0)

        # Encode the filename for Content-Disposition
        encoded_filename = quote(file_name)

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Content-Type": file_mime_type,
        }

        return StreamingResponse(
            file_stream(), headers=headers, media_type=file_mime_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_pdf_page/{file_id}")
def get_pdf_page(
    file_id: str,
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    dpi: int = Query(DEFAULT_DPI, ge=72, le=600, description="DPI for rendering"),
    scale: float = Query(1.0, ge=0.1, le=2.0, description="Scaling factor"),
    color: bool = Query(True, description="Render in color if True, else grayscale"),
):
    try:
        img_byte_arr = pdf_page_to_image(
            file_id=file_id, page=page, dpi=dpi, scale=scale, color=color
        )

        return Response(content=img_byte_arr, media_type="image/png")
    except ValueError as e:
        return Response(content=str(e), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FolderRequest(BaseModel):
    folder_id: str
    force: bool = False
    embed: bool = True


@router.post("/pub-process-folder")
async def pub_process_folder(request: FolderRequest):
    print(f"Processing folder {request.folder_id} with force={request.force}")

    if request.force:
        client = drive_client_factory()
        await client.delete_drive_folder(request.folder_id)

    queue_client = queue_client_factory()
    await queue_client.enqueue(
        JobEvent(
            topic=TOPIC_USER_INPUT_FOLDER,
            data=json.dumps(
                {
                    "folder_id": request.folder_id,
                    "force": request.force,
                    "embed": request.embed,
                }
            ),
        )
    )
    asyncio.create_task(worker_pool.start())
    return {
        "message": f"Drive folder {request.folder_id} processing initiated",
        "status": "success",
        # "items_enqueued": len(items),
    }


class FolderStatusRequest(BaseModel):
    folder_id: str


@router.post("/folder-status")
async def folder_status(request: FolderStatusRequest):
    folder_id = request.folder_id
    print(f"[Folder {folder_id}] Received status request")
    client = drive_client_factory()
    print(f"[Folder {folder_id}] Drive client factory created")

    try:
        print(f"[Folder {folder_id}] Fetching folder")
        folder = await client.get_drive_folder(folder_id)
        print(f"[Folder {folder_id}] Folder status: {folder.status}")

        total_files = len(folder.items)
        embedded_files = sum(
            1
            for status in folder.file_statuses.values()
            if status == DriveFileStatus.EMBEDDED
        )

        response = {
            "status": folder.status.value,
            "message": f"Folder {folder_id} status: {folder.status.value}",
            "updated_at": folder.updated_at,
            "total_files": total_files,
            "embedded_files": embedded_files,
            "processing_files": total_files - embedded_files,
        }

        if folder.status == DriveFolderStatus.DONE:
            response["message"] = f"Folder {folder_id} processing completed"
        elif folder.status == DriveFolderStatus.INTIATED:
            response["message"] = f"Folder {folder_id} processing not started yet"
        elif folder.status == DriveFolderStatus.PROCESSING:
            response["message"] = f"Folder {folder_id} is being processed"

        print(f"[Folder {folder_id}] Response: {response}")
        return response

    except Exception as e:
        print(f"[Folder {folder_id}] Error in folder_status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing folder status: {str(e)}"
        )


@router.post("/start-worker")
async def start_worker(request: FolderRequest):
    print(f"Starting workers for folder {request.folder_id}")

    # Start worker pool (if not already started)
    asyncio.create_task(worker_pool.start())

    return {
        "message": f"Workers started for folder {request.folder_id}",
        "status": "success",
    }


@router.post("/complete-all-jobs")
async def complete_all_jobs():
    """
    清空所有 job queue 裡的 job，開發用
    """
    queue_client = queue_client_factory()
    completed_count = 0

    try:
        while True:
            job = await queue_client.dequeue(all=True)
            if job is None:
                break

            if hasattr(job, "id"):
                await queue_client.complete_job(job.id)
                completed_count += 1

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error completing jobs: {str(e)}")

    return {
        "message": "All jobs completed",
        "status": "success",
        "jobs_completed": completed_count,
    }


class DriveFileRequest(BaseModel):
    file_id: str
    force: bool = False
    # 是否要 embed，這個是做壓測試的時候，可設成 false ，來節省 embed 的金額
    embed: bool = True


@router.post("/process-file")
async def process_file(request: DriveFileRequest):
    # drive_file = DriveFile.from_json(request.drive_file)
    force = request.force
    embed = request.embed

    try:
        drive_client = drive_client_factory()
        drive_file = await drive_client.get_drive_file(request.file_id)
        await _handle_download_and_embed(drive_file, force, embed)
        return {
            "status": "success",
            "message": f"File {drive_file.id} processed successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _handle_download_and_embed(
    drive_file: DriveFile, force: bool, embed: bool = True
):
    folder_path = "./data"
    print(f"_handle_download_and_embed Downloading file: {drive_file.id}")
    drive_file = file_download_with_service(
        get_google_drive_service(), drive_file, folder_path, force=force
    )
    drive_client = drive_client_factory()
    if force:
        drive_file.splitted_files = []
    await drive_client.set_drive_file(drive_file)
    await drive_client.update_drive_file_status_in_folder(
        drive_file.folder_id, drive_file.id, drive_file.status
    )
    await run_split_txts_for_distributed(drive_file, force=force)
    print(f"File: {drive_file.id} splitted")

    if embed:
        embed_success = False
        try:
            print(f"_handle_download_and_embed Embedding file: {drive_file.id}")
            embed_success = await embeddings_to_qdrant_distributed(drive_file)
            print(
                f"_handle_download_and_embed Embedding file: {drive_file.id} done, check success: {embed_success}"
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"Embedding 失敗，錯誤訊息：{e}")
        if embed_success:
            drive_file.status = DriveFileStatus.EMBEDDED
            await drive_client.set_drive_file(drive_file)
            print(
                f"_handle_download_and_embed Folder {drive_file.folder_id} Embedding file: {drive_file.id} set status to embedded"
            )
            await drive_client.update_drive_file_status_in_folder(
                drive_file.folder_id, drive_file.id, drive_file.status
            )

            await _finalize_embed(drive_file)
    else:
        for split_id in drive_file.splitted_files:
            split_file = await drive_client.get_splitted_file(split_id)
            split_file.status = SplittedFileStatus.EMBEDDED
            await drive_client.set_splitted_file(split_file)
        drive_file.status = DriveFileStatus.EMBEDDED
        await drive_client.set_drive_file(drive_file)
        await drive_client.update_drive_file_status_in_folder(
            drive_file.folder_id, drive_file.id, drive_file.status
        )
        await _finalize_embed(drive_file)


async def _finalize_embed(drive_file: DriveFile):
    drive_client = drive_client_factory()
    for item in drive_file.splitted_files:
        split_file = await drive_client.get_splitted_file(item)
        split_file.status = SplittedFileStatus.EMBEDDED
        await drive_client.set_splitted_file(split_file)
        if split_file.save_path:
            try:
                print(f"_finalize_embed Removing split file {split_file.id} save path")
                os.remove(split_file.save_path)
            except Exception as e:
                print(f"Error removing split file {split_file.id} save path: {e}")
    drive_folder = await drive_client.get_drive_folder(drive_file.folder_id)
    all_files_embedded = True
    for file_id in drive_folder.items:
        tmp_drive_file = await drive_client_factory().get_drive_file(file_id)
        if tmp_drive_file.status != DriveFileStatus.EMBEDDED:
            print(
                f"called _finalize_embed from {drive_file.id}, Folder {drive_folder.id} checking File {tmp_drive_file.id} status is not embedded"
            )
            all_files_embedded = False
            break
    if all_files_embedded:
        drive_folder.status = DriveFolderStatus.DONE
        for id, file_status in drive_folder.file_statuses.items():
            drive_folder.file_statuses[id] = DriveFileStatus.EMBEDDED
        print(
            f"called _finalize_embed from {drive_file.id}, All files embedded, updating folder {drive_folder.id} status to done"
        )
        await drive_client.set_drive_folder(drive_folder)
    if drive_file.save_path:
        try:
            print(
                f"called _finalize_embed from {drive_file.id}, Removing drive file {drive_file.id} save path"
            )
            os.remove(drive_file.save_path)
        except Exception as e:
            print(
                f"called _finalize_embed from {drive_file.id}, Error removing drive file {drive_file.id} save path: {e}"
            )
    print(
        f"called _finalize_embed from {drive_file.id},Finalize embed for drive file {drive_file.id}"
    )
