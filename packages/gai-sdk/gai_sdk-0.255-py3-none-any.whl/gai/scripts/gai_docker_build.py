import os
from rich.console import Console
console=Console()
from gai.scripts._docker_utils import _docker_build

def docker_build(project_path,component,no_cache):
    project_path=os.path.abspath(project_path)
    if not project_path.endswith('pyproject.toml'):
        console.print(f"[red]{project_path}[/] does not end with 'pyproject.toml'")
        return
    if not os.path.exists(project_path):
        console.print(f"[red]{project_path}[/] does not exist")
        return
    console.print(f"[yellow]{project_path}[/] exists")
    _docker_build(
        repo='kakkoii1337',
        component_name=component, 
        dockercontext_path=os.path.dirname(project_path),
        no_cache=no_cache)
    print("Docker image built and tagged successfully.")
