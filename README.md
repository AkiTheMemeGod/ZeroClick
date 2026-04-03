# ZeroClick Installer

ZeroClick is a Windows bulk application installer (similar to Ninite) built with Python, FastAPI, and Typer.

## Features

- **CLI Toolkit**: Typer-based CLI for managing apps and installing via command-line.
- **REST API & Web UI**: FastAPI backend with a beautiful HTML/JS frontend to select and install apps with one click.
- **Resumable Downloads**: Powered by `httpx` to handle interrupted downloads cleanly.
- **SQLite Registry**: Local storage for app metadata, with an initial `apps.json` fallback to quickly populate the database.

## Installation

Ensure you have Python 3.11+ installed.

1. Clone or copy the project.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

**Important:** For applications to install silently and properly, you should run this tool using **Administrator privileges**.

### CLI Mode

To view all supported commands:
```bash
python -m app.cli --help
```

Examples:
- List apps: `python -m app.cli list`
- Install specific: `python -m app.cli install git vscode`
- Install all: `python -m app.cli install-all`

### Web API Mode

Start the FastAPI server:
```bash
python -m app.main
```
Or start with `uvicorn`:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Open `http://localhost:8000/` in your browser.

## Converting to `.exe` using PyInstaller

Since this tool will be run on client machines, you might want to package it as a single executable.

```bash
pip install pyinstaller
pyinstaller --name ZeroClick --onefile --add-data "data;data" --add-data "web;web" --add-data "config.yaml;." app/main.py
```
*Note: Make sure to start the generated exe as an administrator.*
