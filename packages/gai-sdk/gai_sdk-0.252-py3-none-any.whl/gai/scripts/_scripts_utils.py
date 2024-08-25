import subprocess
import os
this_dir=os.path.dirname(os.path.realpath(__file__))
from rich.console import Console
console=Console()
import toml

def _cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error: ", e)
        return

def _get_version(pyproject_path):
    data = toml.load(pyproject_path)
    # Extract the version from the [tool.poetry] section
    version = data['tool']['poetry']['version']
    return version