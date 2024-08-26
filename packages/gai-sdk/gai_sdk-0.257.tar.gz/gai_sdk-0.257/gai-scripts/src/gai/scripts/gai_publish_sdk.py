import os
from rich.console import Console
console=Console()
from gai.scripts._scripts_utils import _publish_package
import subprocess

def publish_sdk(env, proj_path):
    try:
        _publish_package(env, proj_path)
    except subprocess.CalledProcessError as e:
        print("An error occurred while publishing package:", e)