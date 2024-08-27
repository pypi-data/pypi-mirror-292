import asyncio
import aiohttp
import time
from typing import Dict, Any
from .emoji_progress_bar import EmojiProgressBar

API_URL = "https://botrun-ask-folder-fastapi-thrhobrjtq-de.a.run.app/api/botrun/botrun_ask_folder"
API_TIMEOUT = 60
CHECK_INTERVAL = 30


async def process_folder_from_restapi(folder_id: str, force: bool = False):
    async with aiohttp.ClientSession() as session:
        # Start processing the folder
        process_url = f"{API_URL}/pub-process-folder"
        data = {"folder_id": folder_id, "force": force, "embed": True}

        async with session.post(
            process_url, json=data, timeout=API_TIMEOUT
        ) as response:
            initial_response = await response.json()
            if initial_response.get("status") == "success":
                print(f"開始執行資料 {folder_id} 匯入工作")
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
                    print(f"{folder_id} 資料匯入完成")
                    return

            except asyncio.TimeoutError:
                print(f"檢查匯入工作 {folder_id} 逾時")
            except Exception as e:
                print(f"檢查匯入工作 {folder_id} 失敗: {str(e)}")


def process_folder(folder_id: str, force: bool = False) -> Dict[str, Any]:
    return asyncio.run(process_folder_from_restapi(folder_id, force))


# Example usage
