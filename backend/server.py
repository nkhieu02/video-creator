from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import os
from video_creator.utils.websocket_manager import WebSocketManager
from contextlib import asynccontextmanager
from .utils import *

class ResearchRequest(BaseModel):
    task: str
    report_type: str
    agent: str


app = FastAPI()

app.mount("/site", StaticFiles(directory="./frontend"), name="site")
app.mount("/static", StaticFiles(directory="./frontend/static"), name="static")

templates = Jinja2Templates(directory="./frontend")

manager = WebSocketManager()


# Dynamic directory for outputs once first research is run

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.isdir("resources/components"):
        os.makedirs("resources/components")
    app.mount("/resources/components", StaticFiles(directory="resources/components"), name="outputs")
    yield

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request, "report": None})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            remove_files_in_directory("/resources/components")
            if data.startswith("start"):
                json_data = json.loads(data[6:])
                blog = json_data.get("blog")
                purpose = json_data.get("purpose")
                platform = json_data.get("platform")
                target_audience = json_data.get("target_audience")
                if blog and purpose and platform and target_audience:
                    report = await manager.start_streaming(blog=blog, purpose=purpose,
                                                           platform=platform, target_audience=target_audience)
                else:
                    print("Error: not enough parameters provided.")

    except WebSocketDisconnect:
        await manager.disconnect(websocket)

