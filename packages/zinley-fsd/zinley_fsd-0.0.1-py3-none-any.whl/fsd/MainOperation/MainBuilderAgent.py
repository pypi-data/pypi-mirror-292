import os
import aiohttp
import json
import sys
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fsd.util.utils import clean_json
from json_repair import repair_json
from fsd.log.logger_config import get_logger

logger = get_logger(__name__)

class MainBuilderAgent:
    def __init__(self, directory_path: str, api_key: str, endpoint: str, deployment_id: str, max_tokens: int):
        self.directory_path = directory_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def scan_txt_files(self) -> List[str]:
        """Scan for all txt files in the specified directory."""
        if not os.path.exists(self.directory_path):
            logger.debug(f"Directory does not exist: {self.directory_path}")
            return []

        return [
            os.path.join(root, file)
            for root, _, files in os.walk(self.directory_path)
            for file in files if file.endswith('.txt')
        ]

    def read_file_content(self, file_path: str) -> Optional[str]:
        """Read the content of a specified file."""
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            logger.info(f"Failed to read file {file_path}: {e}")
            return None

    async def get_pipeline_plan(self, session: aiohttp.ClientSession, files: str, tree: str, directory: str) -> Dict:
        """Get a development plan for all txt files from Azure OpenAI based on the user prompt."""
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a builder agent tasked with checking for any compile errors. "
                        "Analyze the provided context to determine the appropriate pipeline to use and respond in JSON format. "
                        "Follow these guidelines:\n\n"
                        "1. Use pipeline 1 if the project needs to be built with Apple Xcode.\n"
                        "2. Use pipeline 2 if the project can be built without Apple Xcode.\n"
                        "The JSON response must follow this format:\n\n"
                        '{\n    "pipeline": "1 or 2"\n}\n\n'
                        "Return only a valid JSON response without additional text or Markdown symbols."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Here are the file changes that need to be built to verify:\n{files}\n"
                        f"Here is the tree structure of the build project:\n{tree}\n"
                    )
                }
            ],
            "max_tokens": self.max_tokens
        }

        url = f"{self.endpoint}/openai/deployments/{self.deployment_id}/chat/completions?api-version=2024-04-01-preview"

        async with session.post(url, headers=self.headers, json=payload) as response:
            if response.status != 200:
                response_json = await response.json()
                error_message = response_json.get('error', {}).get('message', 'Unknown error')
                return {"reason": error_message}

            plan = await response.json()

            if 'choices' in plan and plan['choices']:
                message_content = plan['choices'][0]['message']['content']
                try:
                    return json.loads(message_content)
                except json.JSONDecodeError:
                    return json.loads(repair_json(message_content))

    async def get_pipeline_plans(self, files: List[str], tree: str, directory: str) -> Dict:
        """Get development plans for a list of txt files from Azure OpenAI based on the user prompt."""
        all_file_contents = "\n\n".join(
            f"File: {file_path}:\n{content}" 
            for file_path in tree 
            if (content := self.read_file_content(file_path))
        )

        async with aiohttp.ClientSession() as session:
            return await self.get_pipeline_plan(session, files, all_file_contents, directory)