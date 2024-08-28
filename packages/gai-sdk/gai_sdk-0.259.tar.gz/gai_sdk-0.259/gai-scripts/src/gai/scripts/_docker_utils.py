import subprocess
import os,sys
this_dir=os.path.dirname(os.path.realpath(__file__))
from rich.console import Console
console=Console()

from ._scripts_utils import _cmd, _get_version, _update_version

def _docker_container_exists(container_name):
    try:
        # Execute docker ps to list all containers
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        # Check if the specified container name is in the output
        return container_name in result.stdout.split()
    except subprocess.CalledProcessError:
        # If there is an error executing docker ps, assume the container does not exist
        return False
    
def _docker_image_exists(image_name):
    try:
        # Execute docker images to list all images
        result = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True,
            check=True
        )
        # Check if the specified image name is in the output
        return image_name in result.stdout.split('\n')
    except subprocess.CalledProcessError:
        # If there is an error executing docker images, assume the image does not exist
        return False        
    
def _docker_build(repo,
                component_name,
                dockercontext_path, 
                dockerfile_path=None, 
                no_cache=False):

    if not dockerfile_path:
        dockerfile_path = f"{dockercontext_path}/Dockerfile"
    version = _update_version(f"{dockercontext_path}/pyproject.toml")    

    # build  
    versioned_image=f"{repo}/{component_name}:{version}"      
    console.print(f"""[yellow]**Build {versioned_image}**[/]""")
    if no_cache:
        console.print(f"""[blue]--no-cache[/]""")
    console.print(f"""[white]dockerfile: {dockerfile_path}[/]""")
    console.print(f"""[white]context: {dockercontext_path}[/]""")
    if _docker_image_exists(versioned_image):
        console.print(f"""[white]Removing existing {versioned_image}[/]""")
        _cmd(f"""docker rmi -f {versioned_image}""")
    cmd=f"""docker buildx build """ + ("""--no-cache""" if no_cache else "") + f""" \
        --progress=plain \
        -f {dockerfile_path} \
        -t {versioned_image} \
        {dockercontext_path}"""
    _cmd(cmd)

    latest_image=f"{repo}/{component_name}:latest"
    if _docker_image_exists(latest_image):
        _cmd(f"docker rmi {latest_image}")
    _cmd(f"docker tag {versioned_image} {latest_image}")
    
    console.print(f"""[green bold]Build {component_name}:{version} Done[/]""")

def _docker_stop(component_name):
    if _docker_container_exists(component_name):
        console.print(f"""[yellow]**Stopping {component_name}**[/]""")
        _cmd(f"""docker stop {component_name}""")
        _cmd(f"""docker rm -f {component_name}""")
        console.print(f"""[bold green]**Docker container {component_name} stopped.[/]""")

def _docker_logs(component_name):
    _cmd(f"""docker logs {component_name}""")

def _docker_idle(repo, component_name):
    _cmd(f"""docker run -d -v ~/.gai:/app/.gai --gpus all --name {component_name} {repo}/{component_name}:latest 
         bash -c "while true; do sleep 1000; done"
         """)

def _docker_ssh(component_name):
    _cmd(f"docker exec -it {component_name} bash")

def _docker_pull(repo, component_name, version=None):
    _cmd(f"docker pull {repo}/{component_name}:latest")
    if version:
        _cmd(f"docker pull {repo}/{component_name}:{version}")

def _docker_push(repo, component_name, project_path):
    version = _get_version(project_path)
    versioned_image=f"{repo}/{component_name}:{version}"
    _cmd(f"docker push {versioned_image}")
    console.print(f"""[green bold]Push {versioned_image} Done[/]""")
    latest_image=f"{repo}/{component_name}:latest"
    _cmd(f"docker push {latest_image}")
    console.print(f"""[green bold]Push {latest_image} Done[/]""")

def _docker_rmi(repo, component_name,version=None):
    _cmd(f"docker rmi {repo}/{component_name}:latest")
    if version:
        _cmd(f"docker rmi {repo}/{component_name}:{version}")