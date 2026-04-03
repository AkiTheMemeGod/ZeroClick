import sqlite3
import json
from pathlib import Path
from typing import List, Optional
from app.models import AppModel
from app.utils import config, logger

DB_PATH = Path(config["data_dir"]) / "database.db"
JSON_PATH = Path(config["data_dir"]) / "apps.json"

def init_db():
    """Initialize SQLite database and populate from JSON if empty."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apps (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            download_url TEXT NOT NULL,
            silent_args TEXT NOT NULL,
            file_type TEXT NOT NULL,
            hash TEXT,
            category TEXT,
            icon_url TEXT
        )
    ''')
    conn.commit()

    # Migration check
    cursor.execute("PRAGMA table_info(apps)")
    columns = [column[1] for column in cursor.fetchall()]
    if "icon_url" not in columns:
        logger.info("Migrating database: Adding icon_url column to apps table")
        cursor.execute("ALTER TABLE apps ADD COLUMN icon_url TEXT")
        conn.commit()

    # Check if empty
    cursor.execute("SELECT COUNT(*) FROM apps")
    if cursor.fetchone()[0] == 0:
        logger.info("Database is empty. Attempting to load from apps.json")
        if JSON_PATH.exists():
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                apps_data = json.load(f)
                for app_data in apps_data:
                    app = AppModel(**app_data)
                    cursor.execute('''
                        INSERT OR REPLACE INTO apps (id, name, download_url, silent_args, file_type, hash, category, icon_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (app.id, app.name, app.download_url, app.silent_args, app.file_type, app.hash, app.category, app.icon_url))
                conn.commit()
            logger.info("Successfully loaded apps from JSON.")
        else:
            logger.warning(f"JSON fallback not found at {JSON_PATH}")

    conn.close()

def get_all_apps() -> List[AppModel]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apps")
    rows = cursor.fetchall()
    conn.close()
    return [AppModel(**dict(row)) for row in rows]

def get_app(app_id: str) -> Optional[AppModel]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apps WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return AppModel(**dict(row))
    return None

def add_app(app: AppModel) -> bool:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO apps (id, name, download_url, silent_args, file_type, hash, category, icon_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (app.id, app.name, app.download_url, app.silent_args, app.file_type, app.hash, app.category, app.icon_url))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error while adding app {app.id}: {e}")
        return False
    finally:
        conn.close()
