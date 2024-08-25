import os
from rich.console import Console
console=Console()
from gai.scripts._docker_utils import _docker_push

def docker_push(project_path, component):
    project_path=os.path.abspath(project_path)
    if not project_path.endswith('pyproject.toml'):
        console.print(f"[red]{project_path}[/] does not end with 'pyproject.toml'")
        return
    if not os.path.exists(project_path):
        console.print(f"[red]{project_path}[/] does not exist")
        return
    console.print(f"[yellow]{project_path}[/] exists")

    _docker_push(
        repo='kakkoii1337',
        component_name=component,
        project_path=project_path)
    
