from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse # Import this
from pydantic import BaseModel
from scrubber import run_scrubber
import os

app = FastAPI()

DOWNLOADS_DIR = "/downloads"

class VideoRequest(BaseModel):
    url: str

@app.post("/api/scrub") # specific prefix helps nginx matching
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

# NEW: Endpoint to serve the file
@app.get("/api/download/{filename}")
async def download_file(filename: str):
    # Sanitize filename to prevent directory traversal attacks (e.g. ../../etc/passwd)
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(DOWNLOADS_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=safe_filename,
        media_type='application/octet-stream' # Forces download behavior
    )