
<h1 align="center">Isometric</h1>

Isometric is a comprehensive CLI (command-line interface) tool that allows researchers to clone and recreate research-oriented GitHub repositories with a simple command, clonong the repository in a virtual environment with installed dependencies and a local LLM that infers necessary libaries/tools. 

Isometric targets common pain points for researcher trying to replicate and clone code for their own experimentation, such as mismatched Python versions, CUDA requirements, or even entirely missing library versions.

# Pipeline Steps
![Flowchart Image](/iso/flowchart.png)

# Quick Run

To quickly clone a repository run the following command

```powershell
iso recreate <github-link>
```
# Requirements
To run Isometric, you'll need:

- Python 3.10+
- Git
- Conda (preferably Miniconda)
- Ollama (or any local LLM model)
- Network/WiFi access.

<br>

# Installation

1. Clone the repo (rayaanmirkar/isometric)
Clone:
  ```powershell
  git clone https://github.com/rayaanmirkar/isometric
  cd isometric
  ```
    
2. Install Isometric:
From the project's root folder:
```powershell
   pip install -e .
```
This will register the iso command.

3. (Optional) Install and Start Ollama for LLM inferences:
```powershell
#First, download Ollama from https://ollama.com, then run the following:
ollama pull qwen2.5-coder:14b
ollama serve
```
If not installed, Isometric will simply skip inferring dependencies.

# Errors
If there are any errors, please pull a request on GitHub, or email at raymirkar@gmail.com.   





