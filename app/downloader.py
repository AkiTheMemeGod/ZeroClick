import os
import httpx
import logging
from typing import Optional
from pathlib import Path
from tqdm import tqdm
from app.utils import config, logger
from app.models import AppModel

DOWNLOAD_DIR = Path(config.get("downloads_dir", "downloads"))

async def download_file(app: AppModel, show_progress: bool = True, on_progress: Optional[callable] = None) -> Optional[Path]:
    """Download an app installer using async HTTP requests with resumption support."""
    url = app.download_url
    filename = f"{app.id}{app.file_type}"
    filepath = DOWNLOAD_DIR / filename
    
    headers = {}
    
    # Check for existing partial download to resume
    if filepath.exists():
        existing_size = filepath.stat().st_size
        headers['Range'] = f"bytes={existing_size}-"
    else:
        existing_size = 0

    try:
        # 30-second connection timeout, 10-minute read timeout for large installers
        timeout = httpx.Timeout(30.0, read=600.0)
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            request = client.build_request("GET", url, headers=headers)
            response = await client.send(request, stream=True)
            
            if response.status_code == 416: # Range Not Satisfiable (Already fully downloaded)
                logger.info(f"{app.name} is already fully downloaded.")
                return filepath
            
            if response.status_code not in (200, 206):
                logger.error(f"Failed to download {app.name}. Status code: {response.status_code}")
                return None
                
            total_size = int(response.headers.get("Content-Length", 0)) + existing_size
            mode = "ab" if response.status_code == 206 else "wb"
            
            if mode == "wb":
                existing_size = 0 # Servers might ignore Range header and send 200 OK

            logger.info(f"Downloading {app.name} to {filepath}...")
            
            with open(filepath, mode) as f:
                with tqdm(
                    total=total_size, 
                    initial=existing_size,
                    unit='B', 
                    unit_scale=True, 
                    unit_divisor=1024,
                    desc=app.name,
                    disable=not show_progress
                ) as pbar:
                    downloaded = existing_size
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        chunk_len = len(chunk)
                        downloaded += chunk_len
                        pbar.update(chunk_len)
                        if on_progress and total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            await on_progress(percent)
                        
            logger.info(f"Successfully downloaded {app.name}")
            return filepath
            
    except Exception as e:
        logger.error(f"Exception while downloading {app.name} ({type(e).__name__}): {e}")
        return None
