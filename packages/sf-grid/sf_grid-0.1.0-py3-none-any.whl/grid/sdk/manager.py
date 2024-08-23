import os
import json
import jwt
import asyncio
import httpx
from typing import Dict, List, Optional
from tabulate import tabulate


class GRIDSessionManager:
    def __init__(self, user_id: str, resource_config_file_path: str) -> None:
        with open(resource_config_file_path, 'r') as f:
            resource_config = json.load(f)

        if 'tokens' not in resource_config or 'resources' not in resource_config:
            raise ValueError("The resource config file must contain 'tokens' and 'resources'.")

        self.resource_data = resource_config
        self.user_id = user_id
        self.platform_auth_token = self.generate_jwt_token(is_platform=True)
        self.session_nodes = {}

    def generate_jwt_token(self, is_platform: bool) -> str:
        secret_key = "rainbowboymonkeysyndromemyelectronicstoremyelectronicstorelastchancetoevacuateplanetearthbeforeitisrecycled"
        payload = {"user_id": self.user_id, "session_id": "test_session"}  # Adjust payload as needed
        return jwt.encode(payload, secret_key, algorithm="HS512")

    def create_config(self, session_config_file_path: str, session_id: str) -> Dict:
        with open(session_config_file_path, 'r') as config_file:
            config_data = json.load(config_file)

        # Check if the required keys exist in the config_data
        if 'airgen' not in config_data or 'grid' not in config_data:
            raise ValueError("The session config file must contain 'airgen' and 'grid' configuration.")

        config_dict = {
            "tokens": self.resource_data["tokens"],
            "user": {"user_id": self.user_id},
            "session": {
                "session_id": session_id,
                "airgen": config_data["airgen"],
                "grid": config_data["grid"],
            },
        }
        return config_dict

    async def start_session(self, session_id: str, resource: str, session_config_file_path: str) -> Optional[bool]:
        print(f"Starting session {session_id} ...")
        config = self.create_config(session_config_file_path, session_id)

        node_ip = self.resource_data["resources"].get(resource)
        if not node_ip:
            print(f"Error: Resource '{resource}' not found in the configuration.")
            return None

        self.session_nodes[session_id] = node_ip  # Store the mapping

        async with httpx.AsyncClient(
            base_url=f"http://{node_ip}:8000", timeout=600
        ) as client:
            try:
                response = await client.post(
                    "/start_session",
                    json={"session_config": config},
                    headers={"Authorization": f"Bearer {self.platform_auth_token}"},
                )
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        print(f"{data['msg_type']}: {data['msg_content']}")
                        if data["msg_type"] == "response_end":
                            if data["success"]:
                                print("Session started successfully.")
                            else:
                                print("Failed to start session.")
                            return data["success"]
            except httpx.RequestError as e:
                print(f"Request error: {e}")
                return None

    async def stop_session(self, session_id: str) -> bool:
        print(f"Stopping session {session_id} ...")

        node_ip = self.session_nodes.get(session_id)
        if not node_ip:
            print(f"No node found for session {session_id}")
            return False

        async with httpx.AsyncClient(
            base_url=f"http://{node_ip}:8000", timeout=600
        ) as client:
            try:
                response = await client.post(
                    "/terminate_session",
                    json={"session_id": session_id, "user_id": self.user_id},
                    headers={"Authorization": f"Bearer {self.platform_auth_token}"},
                )
                response_data = response.json()
                if response_data.get("success"):
                    print("Session stopped successfully.")
                    del self.session_nodes[session_id]  # Remove the mapping
                else:
                    print("Failed to stop session.")
                    print("Response:", response_data)
                return response_data.get("success", False)
            except httpx.RequestError as e:
                print(f"Request error: {e}")
                return False

    async def list_sessions(self) -> List[Dict]:
        if not self.session_nodes:
            print("No active sessions found.")
            return []

        async def get_session_info(session_id: str, node_ip: str) -> Dict:
            async with httpx.AsyncClient(
                base_url=f"http://{node_ip}:8000", timeout=600
            ) as client:
                try:
                    response = await client.get(
                        "/is_idle",
                        params={"session_id": session_id},
                        headers={"Authorization": f"Bearer {self.platform_auth_token}"},
                    )
                    data = response.json()
                    return {
                        "session_id": session_id,
                        "node_ip": node_ip,
                        "is_idle": data.get("is_idle", "N/A"),
                        "last_active_time": data.get("last_active_time", "N/A"),
                    }
                except httpx.RequestError as e:
                    print(f"Request error while fetching session info for {session_id}: {e}")
                    return {
                        "session_id": session_id,
                        "node_ip": node_ip,
                        "is_idle": "Error",
                        "last_active_time": "Error",
                    }

        tasks = [get_session_info(session_id, node_ip) for session_id, node_ip in self.session_nodes.items()]
        session_info_list = await asyncio.gather(*tasks)

        if session_info_list:
            headers = ["Session ID", "Node IP", "Last Active Time"]
            table_data = [
                [info["session_id"], info["node_ip"], info["last_active_time"]]
                for info in session_info_list
            ]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print("No active sessions found.")

        return session_info_list
