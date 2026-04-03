import hashlib
import logging
import sys
import ctypes
import os
import yaml
from pathlib import Path

# Load config
CONFIG_FILE = "config.yaml"
try:
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    config = {
        "downloads_dir": "downloads",
        "logs_dir": "logs",
        "data_dir": "data",
        "parallel_installs": False,
        "logging_level": "INFO"
    }

# Create necessary directories
os.makedirs(config["downloads_dir"], exist_ok=True)
os.makedirs(config["logs_dir"], exist_ok=True)
os.makedirs(config["data_dir"], exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=Path(config["logs_dir"]) / "install.log",
    level=getattr(logging, config["logging_level"].upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ZeroClick")

def is_admin():
    """Check if the script is running with administrator privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def verify_hash(file_path: str, expected_hash: str) -> bool:
    """Verify SHA256 hash of a file."""
    if not expected_hash:
        return True # No hash provided, assume valid
        
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest().lower() == expected_hash.lower()
    except Exception as e:
        logger.error(f"Error verifying hash for {file_path}: {e}")
        return False
