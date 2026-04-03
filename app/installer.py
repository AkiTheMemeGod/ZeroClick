import subprocess
import os
import logging
from pathlib import Path
from typing import Tuple
from app.models import AppModel
from app.utils import logger, is_admin

def install_app(app: AppModel, installer_path: Path) -> Tuple[bool, str]:
    """Execute the installer silently depending on its file type."""
    if not installer_path.exists():
        msg = f"Installer for {app.name} not found at {installer_path}"
        logger.error(msg)
        return False, msg
        
    logger.info(f"Starting installation for {app.name}...")

    try:
        # Determine execution command based on file type
        if app.file_type.lower() == ".msi":
            # For MSI, we typically use msiexec
            cmd = f'msiexec.exe /i "{installer_path.resolve()}" {app.silent_args}'
        else:
            # Assuming .exe by default
            cmd = f'"{installer_path.resolve()}" {app.silent_args}'

        logger.info(f"Executing command: {cmd}")
        
        # We use run and wait for it to finish
        process = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if process.returncode == 0 or process.returncode == 3010: # 3010 is sometimes success/restart needed
            msg = f"Successfully installed {app.name}."
            # Delete the installer after successful installation
            try:
                os.remove(installer_path)
            except Exception as e:
                logger.error(f"Failed to delete installer for {app.name}: {e}")
            logger.info(msg)
            return True, msg
        else:
            msg = f"Installation for {app.name} failed with code {process.returncode}. Error: {process.stderr}"
            logger.error(msg)
            return False, msg

    except Exception as e:
        msg = f"Exception occurred during installation of {app.name}: {e}"
        logger.error(msg)
        return False, msg
