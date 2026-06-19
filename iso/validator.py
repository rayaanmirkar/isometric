import subprocess
import os
from pathlib import Path
from rich.console import Console

console = Console()

def validate_environment(env_name: str, scan_results: dict) -> dict:
    """Validate that the environment works by checking imports."""
    
    console.print(f"[cyan]→ Validating environment[/cyan]")
    
    results = {
        "passed": [],
        "failed": [],
        "warnings": [],
    }

    # extract package names from dependencies (strip version specifiers)
    deps = scan_results.get("dependencies", [])
    packages = []
    for dep in deps:
        # strip version specifiers e.g. "numpy>=1.21" -> "numpy"
        name = dep.split(">=")[0].split("<=")[0].split("==")[0].split("!=")[0].split("[")[0].strip()
        # normalize: torch -> torch, scikit-learn -> sklearn
        name = normalize_import_name(name)
        if name:
            packages.append(name)

    if not packages:
        console.print(f"[yellow]⚠ No packages to validate[/yellow]")
        return results

    # build a validation script
    import_lines = "\n".join([f"import {pkg}" for pkg in packages])
    script = f"""
import sys
results = {{}}
packages = {packages}
for pkg in packages:
    try:
        __import__(pkg)
        results[pkg] = "ok"
    except ImportError as e:
        results[pkg] = f"failed: {{e}}"
    except Exception as e:
        results[pkg] = f"warning: {{e}}"

for pkg, status in results.items():
    print(f"{{pkg}}:{{status}}")
"""

    # write validation script to temp file
    import tempfile
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    tmp.write(script)
    tmp.close()

    # get conda base path
    conda_info = subprocess.run(
        ["conda", "info", "--base"],
        capture_output=True, text=True
    )
    base = conda_info.stdout.strip()
    python = os.path.join(base, "envs", env_name, "python.exe")

    if not os.path.exists(python):
        console.print(f"[red]✗ Could not find Python in environment[/red]")
        return results

    result = subprocess.run(
        [python, tmp.name],
        capture_output=True, text=True
    )
    os.unlink(tmp.name)

    for line in result.stdout.splitlines():
        if ":" in line:
            pkg, status = line.split(":", 1)
            if status == "ok":
                results["passed"].append(pkg)
            elif "failed" in status:
                results["failed"].append((pkg, status))
            else:
                results["warnings"].append((pkg, status))

    # print summary
    console.print(f"[green]✓ {len(results['passed'])} packages validated[/green]")
    if results["failed"]:
        console.print(f"[red]✗ {len(results['failed'])} packages failed:[/red]")
        for pkg, err in results["failed"]:
            console.print(f"    • {pkg}: {err}")
    if results["warnings"]:
        console.print(f"[yellow]⚠ {len(results['warnings'])} warnings[/yellow]")

    return results


def normalize_import_name(name: str) -> str:
    """Normalize package names to their import names."""
    mapping = {
        "scikit-learn": "sklearn",
        "scikit-image": "skimage",
        "pillow": "PIL",
        "opencv-python": "cv2",
        "opencv-python-headless": "cv2",
        "pyyaml": "yaml",
        "beautifulsoup4": "bs4",
        "python-dateutil": "dateutil",
        "tensorflow-intel": "tensorflow",
        "torch-audio": "torchaudio",
    }
    return mapping.get(name.lower(), name.lower().replace("-", "_"))