import requests
import json
from rich.console import Console

console = Console()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:14b"

def infer_missing(scan_results: dict) -> dict:
    """Use Qwen to infer missing environment details from scan results."""
    
    console.print(f"[cyan]→ Inferring missing details with Qwen[/cyan]")

    prompt = f"""You are an expert at analyzing Python research repositories.
Based on the following scan results from a repository, infer any missing environment details.

Scan results:
- Languages: {scan_results['languages']}
- Dependencies found: {scan_results['dependencies']}
- Python version: {scan_results['python_version']}
- CUDA required: {scan_results['cuda']}
- Notebooks: {len(scan_results['notebooks'])} found
- Dockerfiles: {len(scan_results['dockerfiles'])} found

Please respond with ONLY a JSON object containing:
- "python_version": the most likely specific Python version (e.g. "3.10") or null
- "cuda_required": true or false
- "cuda_version": the most likely CUDA version or null
- "missing_dependencies": list of any obvious missing dependencies not in the list
- "notes": any important environment notes

Respond with raw JSON only, no markdown, no explanation."""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        })
        
        raw = response.json()["response"].strip()
        # strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        
        result = json.loads(raw.strip())
        console.print(f"[green]✓ Inference complete[/green]")
        return result

    except Exception as e:
        console.print(f"[yellow]⚠ Inference failed: {e}[/yellow]")
        return {}