import tempfile
import shutil
from pathlib import Path
from git import Repo
from rich.console import Console

console = Console()

def clone_repo(url: str) -> Path:
    """Clone a GitHub repo to a temp directory and return the path."""
    tmp_dir = tempfile.mkdtemp(prefix="iso_")
    path = Path(tmp_dir)
    
    console.print(f"[cyan]→ Cloning[/cyan] {url}")
    Repo.clone_from(url, path)
    console.print(f"[green]✓ Cloned to[/green] {path}")
    
    return path

def cleanup(path: Path):
    """Remove the temp directory."""
    shutil.rmtree(path, ignore_errors=True)