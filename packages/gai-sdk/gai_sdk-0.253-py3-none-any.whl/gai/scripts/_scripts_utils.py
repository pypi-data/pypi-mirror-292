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

def __update_version(pyproject_path):
    with open(pyproject_path, "r+") as f:
        data = toml.load(f)

        # Extract and update the version number
        version_parts = data["tool"]["poetry"]["version"].split(".")
        version_parts[-1] = str(int(version_parts[-1]) + 1)  # Increment the patch version
        data["tool"]["poetry"]["version"] = ".".join(version_parts)

        # Write the updated data back to pyproject.toml
        f.seek(0)
        f.write(toml.dumps(data))
        f.truncate()  # Ensure file is truncated if new data is shorter

        return data["tool"]["poetry"]["version"]
