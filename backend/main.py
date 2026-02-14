from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
from scrubber import run_scrubber
import os
import re

app = FastAPI()

DOWNLOADS_DIR = "/downloads"

class VideoRequest(BaseModel):
    url: str

    @validator('url')
    def validate_url(cls, v):
        if not re.match(r'^https?://', v):
            raise ValueError('URL must start with http:// or https://')
        if not re.match(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', v):
             raise ValueError('Invalid URL format')
        # prevent command injection via argument injection
        if v.startswith('-'):
            raise ValueError('URL cannot start with a dash')
        return v

@app.post("/api/scrub")
async def start_scrub(request: VideoRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_scrubber, request.url)
    return {"status": "started", "message": f"Scrubbing {request.url}"}

@app.get("/api/files")
def list_files():
    # Check if dir exists to prevent crash on fresh start
    if not os.path.exists(DOWNLOADS_DIR):
        return {"files": []}

    files = sorted(os.listdir(DOWNLOADS_DIR), key=lambda x: os.path.getmtime(os.path.join(DOWNLOADS_DIR, x)), reverse=True)
    return {"files": [f for f in files if f.endswith(('.mkv', '.mp4', '.webm'))]}

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    # Sanitize filename to prevent directory traversal attacks (e.g. ../../etc/passwd)
    if os.path.sep in filename or (os.path.altsep and os.path.altsep in filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    safe_filename = os.path.basename(filename)

    # Double check to ensure basename didn't change anything (meaning it was already safe)
    if safe_filename != filename:
         raise HTTPException(status_code=400, detail="Invalid filename traversal attempt")

    file_path = os.path.join(DOWNLOADS_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=safe_filename,
        media_type='application/octet-stream'
    )