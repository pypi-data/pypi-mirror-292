#!/bin/env python3
from pathlib import Path
import json
import sys,os
from openai import OpenAI
from rich.console import Console
from gai.scripts.gai_docker_start import docker_start
from gai.scripts.gai_docker_stop import docker_stop
from gai.scripts.gai_init import init
from gai.scripts.gai_pull import pull

console=Console()

from gai.lib.common.utils import this_dir
here = this_dir(__file__)

def app_dir():
    with open(Path("~/.gairc").expanduser(), "r") as file:
        rc=file.read()
        jsoned = json.loads(rc)
        return Path(jsoned["app_dir"]).expanduser()

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Gai CLI Tool')
    parser.add_argument('command', choices=['init', 'pull', 'news', 'search','docker','chat'], help='Command to run')
    parser.add_argument('-f', '--force', action='store_true', help='Force initialization')
    parser.add_argument('extra_args', nargs='*', help='Additional arguments for commands')

    args = parser.parse_args()

    if args.command == "init":
        print("Initializing...by force" if args.force else "Initializing...")
        init(force=args.force)
    elif args.command == "pull":
        if args.extra_args:
            pull(console, args.extra_args[0])
        else:
            console.print("[red]Model name not provided[/]")
    elif args.command == "docker":
        if args.extra_args:
            if args.extra_args[0] == "start":
                docker_start(here)
            elif args.extra_args[0] == "stop":
                docker_stop(here)
            else:
                console.print("[red]Invalid docker command[/]")
    elif args.command == "news":
        from gai.scripts.gai_news import news
        if args.extra_args:
            news(category=args.extra_args[0])
        else:
            news()
    elif args.command == "search":
        from gai.scripts.gai_search import search
        if args.extra_args:
            search(args.extra_args[0],5)
        else:
            console.print("[red]Search term not provided[/]")
    elif args.command == "chat":
        from gai.scripts.gai_chat import chat
        if args.extra_args:
            chat(args.extra_args[0])
        else:
            console.print("[red]Chat content not provided[/]")

if __name__ == "__main__":
    main()
