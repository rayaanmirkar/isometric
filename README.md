<h1 align="center">Isometric</h1>

Isometric is a comprehensive CLI (command-line interface) tool that allows researchers to clone and recreate research-oriented GitHub repositories with a simple command, clonong the repository in a virtual environment with installed dependencies and a local LLM that infers necessary libaries/tools. 

Isometric targets common pain points for researcher trying to replicate and clone code for their own experimentation, such as mismatched Python versions, CUDA requirements, or even entirely missing library versions.

# Quick Run

To quickly clone a repository run the following command

```powershell

iso recreate <username/repo-name>

```

<h3 align="center">Requirements</h3>

To run Isometric, you need:

- Python 3.10+
- Git
- Conda (preferably Miniconda)
- Ollama (or any local LLM model)
- Network/WiFi access.






