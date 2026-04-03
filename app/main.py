import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi.responses import FileResponse, StreamingResponse
import io
import json
import os

from app.registry import get_all_apps, get_app, add_app, init_db
from app.models import AppModel
from app.downloader import download_file
from app.installer import install_app
from app.utils import verify_hash, is_admin
from app.network import monitor

MARKER = b"###ZEROCLICK_PAYLOAD###"
STUB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "stub.exe")

app = FastAPI(title="ZeroClick API")

# Ensure db is initialized on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Application state for polling
install_status: Dict[str, Dict] = {}

class InstallRequest(BaseModel):
    app_ids: List[str]

@app.get("/apps")
def list_apps():
    """Get list of all supported applications."""
    return get_all_apps()

async def process_install_task(app_id: str):
    app_model = get_app(app_id)
    if not app_model:
        install_status[app_id] = {"status": "error", "message": "App not found", "progress": 0}
        return
        
    async def progress_callback(pct: int):
        install_status[app_id] = {
            "status": "downloading", 
            "message": f"Downloading {app_model.name}... ({pct}%)",
            "progress": pct
        }

    install_status[app_id] = {"status": "downloading", "message": f"Downloading {app_model.name}...", "progress": 0}
    filepath = await download_file(app_model, show_progress=False, on_progress=progress_callback)
    
    if not filepath:
        install_status[app_id] = {"status": "error", "message": "Download failed", "progress": 0}
        return
        
    if app_model.hash:
        install_status[app_id] = {"status": "verifying", "message": "Verifying hash...", "progress": 100}
        if not verify_hash(str(filepath), app_model.hash):
            install_status[app_id] = {"status": "error", "message": "Hash verification failed", "progress": 0}
            return
            
    install_status[app_id] = {"status": "installing", "message": f"Installing {app_model.name}...", "progress": 100}
    
    # Run the installer sync function in a thread to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    success, msg = await loop.run_in_executor(None, install_app, app_model, filepath)
    
    if success:
        install_status[app_id] = {"status": "completed", "message": msg, "progress": 100}
    else:
        install_status[app_id] = {"status": "error", "message": msg, "progress": 0}

@app.post("/install")
async def trigger_install(req: InstallRequest, background_tasks: BackgroundTasks):
    """Trigger installation of requested app IDs."""
    if not is_admin():
        pass # Allow trigger anyway via UI, will emit a warning flag
        
    for app_id in req.app_ids:
        # Avoid restarting if already downloading/installing
        current_status = install_status.get(app_id, {}).get("status")
        if current_status not in ["downloading", "installing"]:
            install_status[app_id] = {"status": "pending", "message": "Waiting to start..."}
            background_tasks.add_task(process_install_task, app_id)
            
    return {"message": "Installation started.", "apps": req.app_ids, "admin": is_admin()}

@app.get("/status")
def get_status():
    """Get status of all installations."""
    return install_status

@app.post("/generate")
async def generate_installer(req: InstallRequest):
    """Generate a custom EXE by appending app data to the stub."""
    if not os.path.exists(STUB_PATH):
        raise HTTPException(status_code=500, detail="Base installer stub not found on server.")
    
    # 1. Collect full app data for selected IDs
    payload_apps = []
    for app_id in req.app_ids:
        app_model = get_app(app_id)
        if app_model:
            payload_apps.append(app_model.dict())
            
    if not payload_apps:
        raise HTTPException(status_code=400, detail="No valid apps selected.")

    # 2. Prepare the payload
    payload_json = json.dumps(payload_apps).encode("utf-8")
    
    # 3. Create the custom binary
    with open(STUB_PATH, "rb") as f:
        stub_data = f.read()
    
    custom_exe = stub_data + MARKER + payload_json
    
    # 4. Stream the file
    return StreamingResponse(
        io.BytesIO(custom_exe),
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=ZeroClickInstaller.exe"}
    )

@app.get("/network-speed")
def get_network_speed():
    """Get current download/upload speed."""
    return monitor.get_speed()

@app.post("/add-app")
def api_add_app(app_data: AppModel):
    if add_app(app_data):
        return {"message": f"Added {app_data.name} successfully."}
    raise HTTPException(status_code=500, detail="Failed to add app to database.")

# Mount web directory
web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
os.makedirs(web_dir, exist_ok=True)

# Mount the static files for the UI
app.mount("/web", StaticFiles(directory=web_dir), name="web")

@app.get("/")
def index():
    return FileResponse(os.path.join(web_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
