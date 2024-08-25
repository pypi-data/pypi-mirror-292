import os
from gai.lib.common.utils import get_gai_config, free_mem
from gai.lib.server.singleton_host import SingletonHost
from rich.console import Console
console = Console()
from gai.lib.common.logging import getLogger
logger = getLogger(__name__)
from gai.lib.server import api_dependencies

# Initialize the fastapi application state

def get_startup_event(app, category, pyproject_toml):

    async def startup_event():
        
        try:
            # check freemem before loading the model
            free_mem()

            # version check
            logger.info(f"Starting Gai LLM Service ({category}) v{api_dependencies.get_app_version(pyproject_toml)}")
            logger.info(f"Version of gai_sdk installed = {api_dependencies.get_sdk_version()}")

            gai_config = get_gai_config()
            
            # extract the default generator config for a category and add it to the app state

            DEFAULT_GENERATOR = gai_config["gen"]["default"][category]
            if os.environ.get("DEFAULT_GENERATOR",None):
                DEFAULT_GENERATOR = os.environ.get("DEFAULT_GENERATOR")
            gai_config = gai_config["gen"][DEFAULT_GENERATOR]
            app.state.gai_config = gai_config

            # initialize host and add it to the app state

            host = SingletonHost.GetInstanceFromConfig(gai_config)
            host.load()
            logger.info(f"Model loaded = [{DEFAULT_GENERATOR}]")
            app.state.host = host

            # check freemem after loading the model
            free_mem()    
        except Exception as e:
            logger.error(f"Failed to load default model: {e}")
            raise e

        app.state.host = host

    return startup_event

def get_shutdown_event(app):
    
    async def shutdown_event():
        host = app.state.host
        if host:
            host.unload()

    return shutdown_event