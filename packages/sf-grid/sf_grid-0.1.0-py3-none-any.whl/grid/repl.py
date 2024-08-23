import asyncio
import os
import subprocess
import webbrowser
import json
import shlex
import logging
from typing import Optional
from cmd import Cmd
from art import tprint
from grid.sdk.manager import GRIDSessionManager

class GRIDRepl(Cmd):
    prompt = 'grid> '
    intro = tprint("\nGRID", "colossal")

    def __init__(self):
        super().__init__()
        self.session_manager: Optional[GRIDSessionManager] = None
        self.loop = asyncio.get_event_loop()
        self._setup_logging()
        print("General Robot Intelligence Development Platform Console \nDeveloped by Scaled Foundations, Inc.\n\n"
              "Type 'help' or 'license' for more info.")

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def cmdloop(self, intro=None):
        while True:
            try:
                super().cmdloop(intro)
                break
            except Exception as e:
                self.logger.error(f"An error occurred: {str(e)}", exc_info=False)
                intro = ''

    def do_exit(self, _):
        """Exit the console."""
        print("Exiting GRID Console...")
        return True

    def do_EOF(self, _):
        """Exit the console on EOF (Ctrl+D)"""
        print("\nExiting GRID Console...")
        return True

    def do_connect(self, arg):
        """Connect to the GRID session manager: connect <user_id> <resource_config_file_path>"""
        args = arg.split()
        if len(args) != 2:
            print("Error: 'connect' command requires exactly two arguments: user_id and resource_config_file_path")
            return
        user_id, resource_config_file_path = args
        self._connect_to_session_manager(user_id, resource_config_file_path)

    def _connect_to_session_manager(self, user_id: str, resource_config_file_path: str):
        self.session_manager = GRIDSessionManager(user_id, resource_config_file_path)
        print(f"Session manager initialized with user ID {user_id} and configuration from {resource_config_file_path}")

    def do_init(self, _):
        """Spin up the GRID containers."""
        self._init_containers()

    def do_terminate(self, _):
        """Terminate the GRID containers."""
        self._kill_containers()

    def do_update(self, _):
        """Update the GRID containers."""
        self._update_containers()

    def do_session(self, arg):
        """Manage sessions:

        session start <session_id> <resource_name> <config_path> : Start a session
        session stop <session_id> : Stop the specified session
        session list : List currently active sessions"""
        if self.session_manager is None:
            print("Session manager not initialized. Use 'connect' command first.")
            return
        args = arg.split()
        if len(args) < 1:
            print("Invalid session command. Use 'session start', 'session stop', or 'session list'.")
            return

        command = args[0]
        if command == 'start' and len(args) == 4:
            self.loop.run_until_complete(self._start_session(args[1], args[2], args[3]))
        elif command == 'stop' and len(args) == 2:
            self.loop.run_until_complete(self._stop_session(args[1]))
        elif command == 'list':
            self.loop.run_until_complete(self._list_sessions())
        else:
            print("Invalid session command.")

    def do_open(self, arg):
        """Open an entity (notebook, simulation, or telemetry): open <resource_name> <nb | sim | viz>"""
        args = arg.split()
        if len(args) < 2:
            print("Invalid open command. Use 'open <session_id> nb | sim | viz'.")
            return
        self._open_entity(args[0], args[1])

    async def _start_session(self, session_id: str, resource: str, config_path: str):
        await self.session_manager.start_session(session_id, resource, config_path)

    async def _stop_session(self, session_id: str):
        await self.session_manager.stop_session(session_id)

    async def _list_sessions(self):
        await self.session_manager.list_sessions()

    @staticmethod
    def _check_docker_container(container_name: str) -> bool:
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], capture_output=True, text=True, check=True)
        return container_name in result.stdout.splitlines()

    def _init_containers(self):
        containers = {
            'grid_core': "docker run -d --gpus all --network host --name grid_core sfgrid.azurecr.io/grid/core/sdk:latest",
            'grid_service': "docker run -d --gpus all --network host --name grid_service sfgrid.azurecr.io/grid/serve/sdk:latest /home/ue4/on_start.sh"
        }

        for container, command in containers.items():
            if not self._check_docker_container(container):
                print(f"Spinning up {container}...")
                subprocess.run(shlex.split(command), check=True)

        if not self._check_docker_container('grid_service') or not self._check_docker_container('grid_core'):
            print("Error: One or more GRID containers failed to start. Please check the logs.")
        else:
            print("Containers are active.")

    def _kill_containers(self):
        print(f"Stopping containers...")
        commands = ["docker stop grid_core", "docker rm grid_core", "docker stop grid_service", "docker rm grid_service"]
        for command in commands:
            subprocess.run(shlex.split(command), check=True)

        if not self._check_docker_container('grid_service') or not self._check_docker_container('grid_core'):
            print("Done.")
        else:
            print("Error: Failed to stop containers.")

    def _update_containers(self):
        print(f"Checking for updates...")
        commands = ["docker pull sfgrid.azurecr.io/grid/core/sdk:latest", "docker pull sfgrid.azurecr.io/grid/serve/sdk:latest"]

        for command in commands:
            subprocess.run(shlex.split(command), check=True)

    def _open_entity(self, session_id: str, entity: str):
        node_ip = self.session_manager.session_nodes[session_id]
        urls = {
            'sim': f"http://{node_ip}:3080",
            'viz': f"http://{node_ip}:9090/?url=ws://{node_ip}:9877",
            'nb': f"http://{node_ip}:8890"
        }

        url = urls.get(entity)
        if url:
            print(f"Opening {entity} for session {session_id} in default browser at {url}")
            webbrowser.open(url)
        else:
            print(f"Unknown entity: {entity}")

def repl():
    GRIDRepl().cmdloop()

if __name__ == "__main__":
    repl()
