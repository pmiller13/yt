from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, validator
from scrubber import run_scrubber
import os
import re
import urllib.parse

app = FastAPI()

DOWNLOADS_DIR = "/downloads"


class VideoRequest(BaseModel):
    url: str

    @validator("url")
    def validate_url(cls, v):
        if not re.match(r"^https?://", v):
            raise ValueError("URL must start with http:// or https://")
        if not re.match(r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", v):
            raise ValueError("Invalid URL format")
        # prevent command injection via argument injection
        if v.startswith("-"):
            raise ValueError("URL cannot start with a dash")
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

    files = sorted(
        os.listdir(DOWNLOADS_DIR),
        key=lambda x: os.path.getmtime(os.path.join(DOWNLOADS_DIR, x)),
        reverse=True,
    )
    return {"files": [f for f in files if f.endswith((".mkv", ".mp4", ".webm"))]}


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    # (Keep your existing path traversal security checks)
    if os.path.sep in filename or (os.path.altsep and os.path.altsep in filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    safe_filename = os.path.basename(filename)

    if safe_filename != filename:
        raise HTTPException(
            status_code=400, detail="Invalid filename traversal attempt"
        )

    file_path = os.path.join(DOWNLOADS_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Encode the filename to handle spaces or special characters in the header
    encoded_filename = urllib.parse.quote(safe_filename)

    # Tell Nginx to take over the download
    headers = {
        # FIX: Ensure the internal Nginx redirect path is fully URL-encoded
        "X-Accel-Redirect": f"/protected-downloads/{encoded_filename}",
        "Content-Type": "application/octet-stream",
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
    }

    # Return an empty body. Nginx will replace it with the actual file!
    return Response(headers=headers)
