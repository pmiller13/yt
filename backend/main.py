from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from scrubber import run_scrubber
import os

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("api/scrub")
async def start_scrub(request: VideoRequest, background_tasks: BackgroundTasks):
    # We run this in the background so the UI doesn't freeze
    background_tasks.add_task(run_scrubber, request.url)
    return {"status": "started", "message": f"Scrubbing {request.url}"}

@app.get("api/files")
def list_files():
    # Simple endpoint to show what's in the folder
    files = sorted(os.listdir("/downloads"), key=lambda x: os.path.getmtime(os.path.join("/downloads", x)), reverse=True)
    return {"files": [f for f in files if f.endswith(('.mkv', '.mp4', '.webm'))]}