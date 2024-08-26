import os
import aiohttp
import asyncio
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import clean_json
from json_repair import repair_json

class TechnicalExplainerAgent:
    def __init__(self, role, directory_path, api_key, endpoint, deployment_id, max_tokens):
        self.directory_path = directory_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.role = role
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def read_file_content(self, file_path):
        """
        Read the content of a given file.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: Content of the file, or None if an error occurs.
        """
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return None

    async def get_technical_plan(self, session, all_file_contents, user_prompt, language):
        """
        Get a development plan for the given prompt from Azure OpenAI.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            user_prompt (str): The user's prompt.

        Returns:
            str: Development plan or error reason.
        """
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are a senior {self.role} and explainer engineering specialist. "
                        "Since Capabilities that AI don’t have right now, we couldn't process what user wants:\n"
                        "- Third party integration\n"
                        "- Create Core data\n"
                        "- Install Networking dependencies like Firebase, AWS\n"
                        "- Create new Test file tasks\n"
                        "Mention your name is Zinley and say apologies to user, explainer guide comprehensively them the best way how to achive their request by.\n"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Project overview:\n{all_file_contents}\n\n"
                        f"User request:\n{user_prompt}\n\n"
                        f"You must respond in this language:\n{language}\n\n"
                    )
                }
            ],
            "temperature": 0.2,
            "top_p": 0.1,
            "max_tokens": self.max_tokens
        }

        url = f"{self.endpoint}/openai/deployments/{self.deployment_id}/chat/completions?api-version=2024-04-01-preview"

        async with session.post(url, headers=self.headers, json=payload) as response:
            if response.status != 200:
                response_json = await response.json()
                error_message = response_json.get('error', {}).get('message', 'Unknown error')
                return {
                    "reason": error_message
                }

            plan = await response.json()

            if 'choices' in plan and len(plan['choices']) > 0:
                message_content = plan['choices'][0]['message']['content']
                return message_content

    async def get_technical_plans(self, files, user_prompt, language):
        """
        Get development plans based on the user prompt.

        Args:
            user_prompt (str): The user's prompt.

        Returns:
            str: Development plan or error reason.
        """
        # Step to remove all empty files from the list
        files = [file for file in files if file]

        all_file_contents = ""

        for file_path in files:
            file_content = self.read_file_content(file_path)
            if file_content:
                all_file_contents += f"\n\nFile: {file_path}:\n{file_content}"

        async with aiohttp.ClientSession() as session:
            plan = await self.get_technical_plan(session, all_file_contents, user_prompt, language)
            return plan
