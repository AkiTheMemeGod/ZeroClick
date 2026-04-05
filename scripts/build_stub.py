import os
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
CLIENT_DIR = ROOT / "client"
DATA_DIR = ROOT / "data"

def sign_exe(exe_path):
    """
    Signs the executable using signtool.exe if a certificate is available.
    Requires Windows SDK and a .pfx certificate.
    """
    cert_path = os.environ.get("SIGNING_CERT_PATH")
    cert_pass = os.environ.get("SIGNING_CERT_PASSWORD")
    
    if not cert_path:
        print("\n[!] Skipping digital signing: SIGNING_CERT_PATH not found in environment.")
        print("Note: Unsigned apps will trigger Windows SmartScreen 'Unknown Publisher' warnings.")
        return False

    signtool = "signtool.exe" # Assumes it's in PATH or Windows SDK is installed
    
    # Common signtool command: 
    # sign /f <cert> /p <pass> /t <timestamp_server> /v <file>
    cmd = [
        signtool,
        "sign",
        "/f", cert_path,
        "/p", cert_pass or "",
        "/t", "http://timestamp.digicert.com", # Standard timestamp server
        "/v",
        str(exe_path)
    ]
    
    print(f"\nSigning {exe_path.name}...")
    try:
        subprocess.run(cmd, check=True)
        print("Successfully signed executable.")
        return True
    except Exception as e:
        print(f"Error during signing: {e}")
        return False

def build():
    print(f"Building ZeroClick stub from {CLIENT_DIR / 'stub.py'}...")
    
    # 1. Clean up build space
    build_dir = ROOT / "build"
    dist_dir = ROOT / "dist"
    for d in [build_dir, dist_dir]:
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)

    # 2. Run PyInstaller
    # --uac-admin: request admin elevation
    # --icon: set the EXE icon
    # --add-data: bundle the UI logo
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole", 
        "--uac-admin",
        "--icon", str(CLIENT_DIR / "assets" / "logo.ico"),
        "--add-data", f"{str(CLIENT_DIR / 'assets')}{os.pathsep}assets",
        "--name", "stub",
        "--clean",
        "--noconfirm",
        str(CLIENT_DIR / "stub.py")
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=ROOT)

    # 3. Sign the EXE (New Optional Step)
    exe_res = dist_dir / "stub.exe"
    if exe_res.exists():
        sign_exe(exe_res)
        
        # 4. Move output to data/ folder
        target = DATA_DIR / "stub.exe"
        print(f"Success! Moving {exe_res} to {target}")
        if target.exists():
            os.remove(target)
        shutil.copy2(exe_res, target)
    else:
        print("Error: stub.exe was not found in dist/ after build.")

    # 5. Final cleanup 
    print("Cleaning up temporary build artifacts...")
    for d in [build_dir, dist_dir]:
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
    
    spec_file = ROOT / "stub.spec"
    if spec_file.exists():
        os.remove(spec_file)

if __name__ == "__main__":
    build()
