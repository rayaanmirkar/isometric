import typer
from rich.console import Console
from iso.cloner import clone_repo
from iso.scanner import scan
from iso.inference import infer_missing
from iso.builder import build_environment
from iso.datasets import find_datasets
from iso.validator import validate_environment
from iso.bundler import create_bundle

app = typer.Typer()
recreate_app = typer.Typer()
app.add_typer(recreate_app, name="recreate")
console = Console()

@recreate_app.callback(invoke_without_command=True)
def recreate(source: str = typer.Argument(..., help="GitHub repo URL, DOI, or bundle path")):
    """Recreate an environment from a GitHub repo, DOI, or bundle."""
    console.print(f"[bold green]isometric[/bold green] — recreating from: {source}")

    path = clone_repo(source)
    results = scan(path)
    inferred = infer_missing(results)

    console.print(f"\n[bold]Languages:[/bold] {', '.join(results['languages'])}")
    console.print(f"[bold]Python version:[/bold] {results['python_version'] or inferred.get('python_version') or 'not specified'}")
    console.print(f"[bold]CUDA required:[/bold] {inferred.get('cuda_required', False)}")
    console.print(f"[bold]Dependencies:[/bold] {len(results['dependencies'])} found")
    console.print(f"[bold]Notes:[/bold] {inferred.get('notes', 'none')}\n")

    env_name = f"iso_{path.name[-6:]}"
    build_environment(env_name, results, inferred)

    dataset_results = find_datasets(path)
    validation_results = validate_environment(env_name, results)

    create_bundle(env_name, results, inferred, dataset_results, validation_results, source)

    console.print(f"\n[bold green]✓ Done![/bold green] Activate with: conda activate {env_name}")

if __name__ == "__main__":
    app()