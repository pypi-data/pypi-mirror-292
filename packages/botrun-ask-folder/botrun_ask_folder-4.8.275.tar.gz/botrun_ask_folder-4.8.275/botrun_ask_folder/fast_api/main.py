from fastapi import FastAPI
from botrun_ask_folder.fast_api.router_botrun_ask_folder import router
from botrun_ask_folder.fast_api.drive_api import (
    drive_api_router,
)
from botrun_ask_folder.fast_api.storage_api import (
    storage_api_router,
)
from botrun_ask_folder.fast_api.queue_api import (
    queue_api_router,
)

app = FastAPI()
api_botrun = FastAPI()


api_botrun.include_router(router)
api_botrun.include_router(drive_api_router)
api_botrun.include_router(storage_api_router)
api_botrun.include_router(queue_api_router)
app.mount("/api/botrun", api_botrun)
