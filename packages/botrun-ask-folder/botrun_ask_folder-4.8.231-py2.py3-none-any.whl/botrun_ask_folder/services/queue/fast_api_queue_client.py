import aiohttp
import os
from typing import Union
from botrun_ask_folder.constants import FAST_API_TIMEOUT
from botrun_ask_folder.fast_api.util.http_request_retry_decorator import async_retry
from botrun_ask_folder.models.job_event import JobEvent
from botrun_ask_folder.services.queue.queue_client import QueueClient

API_PREFIX = "api/botrun/botrun_ask_folder"


class FastAPIQueueClient(QueueClient):
    def __init__(self, api_url: str = os.getenv("FAST_API_URL")):
        self.api_url = api_url

    @async_retry(attempts=3, delay=1)
    async def enqueue(self, job: JobEvent) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/queue/enqueue",
                json=job.model_dump(),
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["job_id"]

    @async_retry(attempts=3, delay=1)
    async def dequeue(self, all: bool = False) -> Union[JobEvent, None]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/{API_PREFIX}/queue/dequeue",
                params={"all": str(all).lower()},
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if "job" not in data:
                    return None
                return JobEvent(**data["job"])

    @async_retry(attempts=3, delay=1)
    async def complete_job(self, job_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/queue/complete/{job_id}",
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()

    @async_retry(attempts=3, delay=1)
    async def fail_job(self, job_id: str, error: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/queue/fail/{job_id}",
                json={"error": error},
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()

    @async_retry(attempts=3, delay=1)
    async def reset_job(self, job_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/{API_PREFIX}/queue/reset/{job_id}",
                timeout=FAST_API_TIMEOUT,
            ) as response:
                response.raise_for_status()
