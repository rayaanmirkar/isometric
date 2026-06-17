import json
from pathlib import Path
from rich.console import Console

console = Console()

DEPENDENCY_FILES = [
    "requirements.txt",
    "requirements/*.txt",
    "environment.yml",
    "environment.yaml",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
]

def scan(repo_path: Path) -> dict:
    """Scan a repo and extract all available environment information."""
    console.print(f"[cyan]→ Scanning[/cyan] {repo_path}")
    
    results = {
        "languages": [],
        "dependency_files": [],
        "dependencies": [],
        "python_version": None,
        "cuda": None,
        "datasets": [],
        "notebooks": [],
        "dockerfiles": [],
    }

    # detect languages
    extensions = [f.suffix for f in repo_path.rglob("*") if f.is_file()]
    if ".py" in extensions:
        results["languages"].append("python")
    if ".r" in extensions or ".R" in extensions:
        results["languages"].append("R")

    # find dependency files
    # find dependency files
    for pattern in DEPENDENCY_FILES:
        if "/" in pattern:
            for match in repo_path.rglob(pattern.split("/")[-1]):
                results["dependency_files"].append(str(match))
                console.print(f"[green]✓ Found[/green] {match.name}")
        else:
            for match in repo_path.rglob(pattern):
                results["dependency_files"].append(str(match))
                console.print(f"[green]✓ Found[/green] {match.name}")

    # find notebooks
    for nb in repo_path.rglob("*.ipynb"):
        results["notebooks"].append(str(nb))
        console.print(f"[green]✓ Found notebook[/green] {nb.name}")

    # find dockerfiles
    for df in repo_path.rglob("Dockerfile*"):
        results["dockerfiles"].append(str(df))
        console.print(f"[green]✓ Found dockerfile[/green] {df.name}")

    # parse dependency files
    for dep_file in results["dependency_files"]:
        p = Path(dep_file)
        if p.name == "requirements.txt":
            deps = parse_requirements(p)
            results["dependencies"].extend(deps)
        elif p.name == "pyproject.toml":
            deps = parse_pyproject(p)
            results["dependencies"].extend(deps)
        elif p.name == "setup.py":
            deps = parse_setup_py(p)
            results["dependencies"].extend(deps)    

    # detect python version
    pyproject_path = repo_path / "pyproject.toml"
    if pyproject_path.exists():
        try:
            import tomllib
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            requires_python = data.get("project", {}).get("requires-python", None)
            if requires_python:
                results["python_version"] = requires_python
        except Exception:
            pass

    runtime_file = repo_path / "runtime.txt"
    if runtime_file.exists():
        try:
            content = runtime_file.read_text().strip()
            if content.startswith("python-"):
                results["python_version"] = content.replace("python-", "")
        except Exception:
            pass

    console.print(f"[green]✓ Scan complete[/green] — found {len(results['dependencies'])} dependencies")
    return results


def parse_requirements(path: Path) -> list:
    """Parse a requirements.txt file and return a list of dependencies."""
    deps = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                deps.append(line)
    except Exception:
        pass
    return deps


def parse_pyproject(path: Path) -> list:
    """Parse a pyproject.toml file and return a list of dependencies."""
    deps = []
    try:
        import tomllib
        with open(path, "rb") as f:
            data = tomllib.load(f)
        project_deps = data.get("project", {}).get("dependencies", [])
        deps.extend(project_deps)
    except Exception:
        pass
    return deps

def parse_setup_py(path: Path) -> list:
    """Extract dependencies from setup.py by reading install_requires."""
    deps = []
    try:
        content = path.read_text(encoding="utf-8")
        import re
        match = re.search(r'install_requires\s*=\s*\[([^\]]+)\]', content, re.DOTALL)
        if match:
            raw = match.group(1)
            for line in raw.splitlines():
                line = line.strip().strip('",\'').strip()
                if line:
                    deps.append(line)
    except Exception:
        pass
    return deps