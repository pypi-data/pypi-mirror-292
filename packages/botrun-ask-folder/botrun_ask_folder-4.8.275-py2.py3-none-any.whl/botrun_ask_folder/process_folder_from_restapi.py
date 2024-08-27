import asyncio
import aiohttp
import time
import os
from typing import Dict, Any

from botrun_ask_folder.embeddings_to_qdrant import has_collection_in_qdrant
from .emoji_progress_bar import EmojiProgressBar
from .botrun_drive_manager import botrun_drive_manager

API_URL = "https://botrun-ask-folder-fastapi-thrhobrjtq-de.a.run.app/api/botrun/botrun_ask_folder"
API_TIMEOUT = 60
CHECK_INTERVAL = 10


async def process_folder_from_restapi(folder_id: str, force: bool = False):
    qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
    qdrant_port = os.getenv("QDRANT_PORT", 6333)
    collection_existed = await has_collection_in_qdrant(
        f"{folder_id}",
        qdrant_host,
        qdrant_port,
    )
    async with aiohttp.ClientSession() as session:
        # Start processing the folder
        process_url = f"{API_URL}/pub-process-folder"
        data = {"folder_id": folder_id, "force": force, "embed": True}

        print(f"開始執行資料 {folder_id} 匯入工作")
        async with session.post(
            process_url, json=data, timeout=API_TIMEOUT
        ) as response:
            initial_response = await response.json()
            if initial_response.get("status") == "success":
                print(f"條列所有 {folder_id} 的檔案")
            else:
                print(f"資料 {folder_id} 匯入工作失敗: 得到訊息 {initial_response}")
                return

        # Initialize EmojiProgressBar
        progress_bar = EmojiProgressBar(total=1)  # Initialize with 1, will update later
        progress_bar.set_description(
            f"{folder_id} 資料匯入中，檢查狀態更新時間：{time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Check status periodically
        status_url = f"{API_URL}/folder-status"
        while True:
            await asyncio.sleep(CHECK_INTERVAL)

            try:
                async with session.post(
                    status_url, json={"folder_id": folder_id}, timeout=API_TIMEOUT
                ) as response:
                    status = await response.json()

                total_files = status.get("total_files", 0)
                embedded_files = status.get("embedded_files", 0)

                # Update progress bar
                if total_files > 0 and embedded_files > 0:
                    progress_bar.total = total_files
                    progress_bar.update(embedded_files)
                    progress_bar.set_description(
                        f"{folder_id} 資料匯入中，檢查狀態更新時間：{time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                elif total_files > 0:
                    print(
                        f"{folder_id} 資料匯入中，檢查狀態更新時間：{time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )

                if status.get("status") == "DONE":
                    if not collection_existed:
                        botrun_drive_manager(
                            f"波{folder_id}", f"{folder_id}", force=force
                        )
                    elif force:
                        botrun_drive_manager(
                            f"波{folder_id}", f"{folder_id}", force=force
                        )
                    else:
                        print(f"{folder_id} 資料匯入完成，可以開始使用")
                    return

            except asyncio.TimeoutError:
                print(f"檢查匯入工作 {folder_id} 逾時")
            except Exception as e:
                print(f"檢查匯入工作 {folder_id} 失敗: {str(e)}")


def process_folder(folder_id: str, force: bool = False) -> Dict[str, Any]:
    return asyncio.run(process_folder_from_restapi(folder_id, force))


# Example usage
