import os
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
CLIENT_DIR = ROOT / "client"
DATA_DIR = ROOT / "data"

def build():
    print(f"Building ZeroClick stub from {CLIENT_DIR / 'stub.py'}...")
    
    # 1. Clean up build space
    build_dir = ROOT / "build"
    dist_dir = ROOT / "dist"
    for d in [build_dir, dist_dir]:
        if d.exists():
            shutil.rmtree(d)

    # 2. Run PyInstaller
    # --onefile: bundle into single exe
    # --console: show console for progress
    # --name stub: name the output stub.exe
    # --clean: clean cache
    cmd = [
        "pyinstaller",
        "--onefile",
        "--console", 
        "--name", "stub",
        "--clean",
        str(CLIENT_DIR / "stub.py")
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=ROOT)

    # 3. Move output to data/ folder
    exe_res = dist_dir / "stub.exe"
    if exe_res.exists():
        target = DATA_DIR / "stub.exe"
        print(f"Success! Moving {exe_res} to {target}")
        if target.exists():
            os.remove(target)
        shutil.copy2(exe_res, target)
    else:
        print("Error: stub.exe was not found in dist/ after build.")

    # 4. Final cleanup 
    print("Cleaning up temporary build artifacts...")
    for d in [build_dir, dist_dir]:
        if d.exists():
            shutil.rmtree(d)
    
    spec_file = ROOT / "stub.spec"
    if spec_file.exists():
        os.remove(spec_file)

if __name__ == "__main__":
    build()
