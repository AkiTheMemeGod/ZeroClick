import json
import sqlite3
from pathlib import Path
import sys
import os

# Add the current directory to path so we can import app
sys.path.append(os.getcwd())

from app.registry import add_app
from app.models import AppModel

JSON_PATH = Path("data/apps.json")

def sync():
    if not JSON_PATH.exists():
        print("Apps JSON not found!")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        apps_data = json.load(f)
        for app_data in apps_data:
            app = AppModel(**app_data)
            if add_app(app):
                print(f"Synced: {app.name}")
            else:
                print(f"Failed to sync: {app.name}")

if __name__ == "__main__":
    sync()
