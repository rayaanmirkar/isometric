import re
import requests
from pathlib import Path
from rich.console import Console

console = Console()

DATASET_PATTERNS = [
    r'https?://[^\s\'"]+\.(?:csv|tsv|zip|tar\.gz|h5|hdf5|pt|pth|pkl|json|parquet)',
    r'(?:download|wget|curl)\s+["\']?(https?://[^\s\'"]+)["\']?',
    r'(GSE\d+)',
    r'(SRP\d+|SRR\d+)',
    r'zenodo\.org/record/\d+',
    r'huggingface\.co/datasets/[\w\-/]+',
    r'kaggle\.com/datasets/[\w\-/]+',
]

def find_datasets(repo_path: Path) -> dict:
    """Find dataset references in a repository."""
    console.print(f"[cyan]→ Scanning for datasets[/cyan]")

    results = {
        "urls": [],
        "accessions": [],
        "huggingface": [],
        "kaggle": [],
        "dead_links": [],
    }

    scan_files = []
    for pattern in ["*.md", "*.txt", "*.py", "*.ipynb", "*.sh"]:
        scan_files.extend(repo_path.rglob(pattern))

    seen = set()

    for file in scan_files:
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
            for pattern in DATASET_PATTERNS:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    if match and match not in seen:
                        seen.add(match)
                        categorize(match, results)
        except Exception:
            continue

    total = sum(len(v) for v in results.values())
    console.print(f"[green]✓ Found {total} dataset references[/green]")

    if results["huggingface"]:
        console.print(f"[cyan]  HuggingFace:[/cyan]")
        for ds in results["huggingface"]:
            console.print(f"    • {ds}")

    if results["accessions"]:
        console.print(f"[cyan]  GEO/SRA accessions:[/cyan]")
        for acc in results["accessions"]:
            console.print(f"    • {acc}")

    if results["kaggle"]:
        console.print(f"[cyan]  Kaggle:[/cyan]")
        for ds in results["kaggle"]:
            console.print(f"    • {ds}")

    if results["urls"]:
        console.print(f"[cyan]  Direct URLs:[/cyan]")
        for url in results["urls"][:5]:
            console.print(f"    • {url}")
    
    return results


def categorize(match: str, results: dict):
    """Categorize a dataset reference."""
    m = match.lower()
    if "huggingface.co/datasets" in m:
        results["huggingface"].append(match)
    elif "kaggle.co" in m:
        results["kaggle"].append(match)
    elif re.match(r'(GSE|SRP|SRR)\d+', match, re.IGNORECASE):
        results["accessions"].append(match)
    elif match.startswith("http"):
        results["urls"].append(match)


def check_url(url: str) -> bool:
    """Check if a URL is accessible."""
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        return r.status_code < 400
    except Exception:
        return False