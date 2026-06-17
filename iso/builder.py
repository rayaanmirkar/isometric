import subprocess
import shutil
import os
import tempfile
from rich.console import Console

console = Console()

def get_conda_path() -> str:
    """Find conda executable."""
    conda = shutil.which("conda")
    if conda:
        return conda
    candidates = [
        os.path.expanduser("~/miniconda3/Scripts/conda.exe"),
        os.path.expanduser("~/anaconda3/Scripts/conda.exe"),
        "C:/ProgramData/miniconda3/Scripts/conda.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "conda"

CONDA = get_conda_path()

def get_env_pip(env_name: str) -> str:
    """Get the pip path inside a conda environment on Windows."""
    conda_info = subprocess.run(
        [CONDA, "info", "--base"],
        capture_output=True, text=True
    )
    base = conda_info.stdout.strip()
    pip = os.path.join(base, "envs", env_name, "Scripts", "pip.exe")
    if os.path.exists(pip):
        return pip
    return None

def build_environment(env_name: str, scan_results: dict, inferred: dict) -> bool:
    """Create a conda environment with the detected dependencies."""
    
    # determine python version
    python_version = scan_results.get("python_version") or inferred.get("python_version") or "3.10"
    python_version = python_version.replace(">=", "").replace("<=", "").replace("==", "").strip()
    parts = python_version.split(".")
    # validate - if minor version is not a number, default to 3.10
    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) >= 2 else 10
        python_version = f"{major}.{minor}"
    except (ValueError, IndexError):
        python_version = "3.10"

    console.print(f"[cyan]→ Creating conda environment:[/cyan] {env_name} (Python {python_version})")

    result = subprocess.run(
        [CONDA, "create", "-n", env_name, f"python={python_version}", "-y"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        console.print(f"[red]✗ Failed to create environment[/red]")
        console.print(result.stderr)
        return False

    console.print(f"[green]✓ Environment created[/green]")

    deps = scan_results.get("dependencies", [])
    if not deps:
        console.print(f"[yellow]⚠ No dependencies to install[/yellow]")
        return True

    # write deps to a temp requirements file
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    tmp.write("\n".join(deps))
    tmp.close()

    pip = get_env_pip(env_name)
    if not pip:
        console.print(f"[red]✗ Could not find pip in environment[/red]")
        return False

    console.print(f"[cyan]→ Installing {len(deps)} dependencies[/cyan]")
    result = subprocess.run(
        [pip, "install", "-r", tmp.name],
        capture_output=False
    )

    os.unlink(tmp.name)

    if result.returncode != 0:
        console.print(f"[yellow]⚠ Some dependencies failed to install[/yellow]")
    else:
        console.print(f"[green]✓ Dependencies installed[/green]")

    return True