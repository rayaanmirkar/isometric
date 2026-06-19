import json
import shutil
import subprocess
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console

console = Console()

def create_bundle(env_name: str, scan_results: dict, inferred: dict, dataset_results: dict, validation_results: dict, source: str) -> Path:
    """Package everything into a portable .iso bundle."""
    
    console.print(f"[cyan]→ Creating bundle[/cyan]")

    bundle_name = f"{env_name}.iso"
    bundle_path = Path.cwd() / bundle_name
    bundle_path.mkdir(exist_ok=True)

    # get pinned package versions from the environment
    conda_info = subprocess.run(
        ["conda", "info", "--base"],
        capture_output=True, text=True
    )
    base = conda_info.stdout.strip()
    pip = os.path.join(base, "envs", env_name, "Scripts", "pip.exe")

    pinned_deps = []
    if os.path.exists(pip):
        result = subprocess.run(
            [pip, "freeze"],
            capture_output=True, text=True
        )
        pinned_deps = result.stdout.strip().splitlines()

    # write pinned requirements
    req_file = bundle_path / "requirements.pinned.txt"
    req_file.write_text("\n".join(pinned_deps))

    # write manifest
    manifest = {
        "version": "0.1.0",
        "created": datetime.now().isoformat(),
        "source": source,
        "python_version": scan_results.get("python_version") or inferred.get("python_version") or "3.10",
        "cuda_required": inferred.get("cuda_required", False),
        "cuda_version": inferred.get("cuda_version", None),
        "dependencies": scan_results.get("dependencies", []),
        "pinned_dependencies": pinned_deps,
        "datasets": dataset_results,
        "validation": {
            "passed": validation_results.get("passed", []),
            "failed": [p for p, _ in validation_results.get("failed", [])],
        },
        "notes": inferred.get("notes", ""),
    }

    manifest_file = bundle_path / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2))

    # write environment.yml
    env_yml = bundle_path / "environment.yml"
    result = subprocess.run(
        ["conda", "env", "export", "-n", env_name],
        capture_output=True, text=True
    )
    env_yml.write_text(result.stdout)

    # write README
    readme = bundle_path / "README.md"
    readme.write_text(f"""# Isometric Bundle

**Source:** {source}
**Created:** {manifest['created']}
**Python:** {manifest['python_version']}
**CUDA:** {manifest['cuda_required']}

## Recreate

```bash
iso recreate {bundle_name}
```

## Dependencies
{chr(10).join(f"- {d}" for d in pinned_deps[:20])}

## Notes
{manifest['notes']}
""")

    console.print(f"[green]✓ Bundle created:[/green] {bundle_name}/")
    console.print(f"  • manifest.json")
    console.print(f"  • requirements.pinned.txt ({len(pinned_deps)} packages)")
    console.print(f"  • environment.yml")
    console.print(f"  • README.md")

    return bundle_path