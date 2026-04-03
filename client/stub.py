import os
import sys
import json
import asyncio
import httpx
import subprocess
import tempfile
import shutil
from pathlib import Path
import time

# Unique marker used to find the JSON payload appended to the EXE
MARKER = b"###ZEROCLICK_PAYLOAD###"

class ZeroClickStub:
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="zeroclick_"))
        self.apps = []

    def load_payload(self):
        try:
            exe_path = sys.executable
            # In development, check for a local payload.json for testing
            if not getattr(sys, 'frozen', False):
                payload_path = Path(__file__).parent / "payload.json"
                if payload_path.exists():
                    self.apps = json.loads(payload_path.read_text())
                    return True
            
            with open(exe_path, "rb") as f:
                content = f.read()
                if MARKER in content:
                    _, payload_str = content.split(MARKER, 1)
                    self.apps = json.loads(payload_str.decode('utf-8'))
                    return True
        except Exception as e:
            print(f"Error loading payload: {e}")
        return False

    async def download_file(self, app, client):
        url = app['download_url']
        filename = f"{app['id']}{app['file_type']}"
        filepath = self.temp_dir / filename
        
        print(f"Downloading {app['name']}...")
        try:
            async with client.stream("GET", url, follow_redirects=True) as response:
                if response.status_code != 200:
                    print(f"  Failed: HTTP {response.status_code}")
                    return None
                
                with open(filepath, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
            return filepath
        except Exception as e:
            print(f"  Download error: {e}")
            return None

    def install_app(self, app, filepath):
        print(f"Installing {app['name']}...")
        try:
            # Basic elevation check or just run (Windows will prompt if needed)
            cmd = f'"{filepath}" {app["silent_args"]}'
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if process.returncode == 0:
                print(f"  Successfully installed.")
                return True
            else:
                print(f"  Installation finished with code {process.returncode}")
                return True # Many installers return non-zero but succeed
        except Exception as e:
            print(f"  Installation error: {e}")
            return False

    async def run(self):
        print("========================================")
        print("       ZeroClick Silent Installer       ")
        print("========================================")
        
        if not self.load_payload():
            print("Error: No installation payload found in this executable.")
            print("Please generate a valid installer from the ZeroClick dashboard.")
            time.sleep(5)
            return

        print(f"Found {len(self.apps)} apps to install.")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            for app in self.apps:
                filepath = await self.download_file(app, client)
                if filepath:
                    self.install_app(app, filepath)
                    # Small delay to prevent overlap issues
                    time.sleep(1)
        
        print("\nAll tasks completed!")
        print("Cleaning up...")
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
        print("The installer will close in 5 seconds.")
        time.sleep(5)

if __name__ == "__main__":
    stub = ZeroClickStub()
    asyncio.run(stub.run())
