import typer
import asyncio
from typing import List
from rich.console import Console
from rich.table import Table
from app.registry import get_all_apps, get_app, add_app, init_db
from app.downloader import download_file
from app.installer import install_app
from app.models import AppModel
from app.utils import verify_hash, is_admin, logger

console = Console()
app = typer.Typer(help="ZeroClick - Silent Windows Application Installer")

@app.command("list")
def list_apps():
    """List all available applications in the registry."""
    apps = get_all_apps()
    if not apps:
        console.print("[yellow]No apps found in registry. Running initialization...[/yellow]")
        init_db()
        apps = get_all_apps()
        
    table = Table(title="Available Applications")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Category", style="green")
    
    for a in apps:
        table.add_row(a.id, a.name, a.category or "N/A")
        
    console.print(table)

async def _process_install(app_model: AppModel):
    filepath = await download_file(app_model, show_progress=True)
    if not filepath:
        console.print(f"[red]Failed to download {app_model.name}[/red]")
        return
        
    if app_model.hash:
        console.print(f"[cyan]Verifying hash for {app_model.name}...[/cyan]")
        if not verify_hash(str(filepath), app_model.hash):
            console.print(f"[red]Hash verification failed for {app_model.name}! Aborting.[/red]")
            return
            
    console.print(f"[cyan]Installing {app_model.name}...[/cyan]")
    success, msg = install_app(app_model, filepath)
    if success:
        console.print(f"[green]✔ {msg}[/green]")
    else:
        console.print(f"[red]✖ {msg}[/red]")

@app.command("install")
def install(app_ids: List[str]):
    """Install selected apps by their IDs."""
    if not is_admin():
        console.print("[bold yellow]Warning: You are not running as Administrator. Some installations may fail.[/bold yellow]")
        
    apps = []
    for app_id in app_ids:
        app_model = get_app(app_id)
        if not app_model:
            console.print(f"[red]App ID '{app_id}' not found.[/red]")
            continue
        apps.append(app_model)
        
    if not apps:
        return
        
    for app_model in apps:
        asyncio.run(_process_install(app_model))

@app.command("install-all")
def install_all():
    """Install ALL available applications in the registry."""
    if not is_admin():
        console.print("[bold yellow]Warning: You are not running as Administrator. Some installations may fail.[/bold yellow]")
        
    apps = get_all_apps()
    for app_model in apps:
        asyncio.run(_process_install(app_model))

@app.command("update")
def update(app_ids: List[str] = typer.Argument(None)):
    """Re-run the installer for the provided apps (or all apps if none provided) to update them."""
    if not app_ids:
        console.print("[cyan]Updating all apps...[/cyan]")
        install_all()
    else:
        install(app_ids)

@app.command("add-app")
def add_new_app(
    id: str = typer.Option(..., prompt=True),
    name: str = typer.Option(..., prompt=True),
    url: str = typer.Option(..., prompt="Download URL"),
    args: str = typer.Option(..., prompt="Silent Args"),
    ext: str = typer.Option(..., prompt="File Extension (e.g., .exe)"),
    cat: str = typer.Option("Utilities", prompt="Category"),
    file_hash: str = typer.Option("", prompt="SHA256 Hash (optional)")
):
    """Add a new custom app to the registry."""
    new_app = AppModel(
        id=id,
        name=name,
        download_url=url,
        silent_args=args,
        file_type=ext,
        category=cat,
        hash=file_hash if file_hash else None
    )
    if add_app(new_app):
        console.print(f"[green]Successfully added {name} to registry.[/green]")
    else:
        console.print(f"[red]Failed to add {name}.[/red]")
        
if __name__ == "__main__":
    app()
