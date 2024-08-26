import os
import aiohttp
import asyncio
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import clean_json
from json_repair import repair_json

class GeneralExplainerAgent:
    def __init__(self, directory_path, api_key, endpoint, deployment_id, max_tokens):
        self.directory_path = directory_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    async def get_normal_answer_plan(self, session, user_prompt, language):
        """
        Get a development plan for all txt files from Azure OpenAI based on the user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            all_file_contents (str): The concatenated contents of all files.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Your name is Zinley, an iOS developer\n\n"
                        "You need to reply to user prompt and repond in provided request language\n\n"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"User prompt:\n{user_prompt}\n\n"
                        f"You must respond in this language:\n{language}\n\n"
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
                return {
                    "reason": error_message
                }

            plan = await response.json()

            if 'choices' in plan and len(plan['choices']) > 0:
                message_content = plan['choices'][0]['message']['content']
                return message_content

    async def get_normal_answer_plans(self, user_prompt, language):
        """
        Get development plans for a list of txt files from Azure OpenAI based on the user prompt.

        Args:
            files (list): List of file paths.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """

        async with aiohttp.ClientSession() as session:
            plan = await self.get_normal_answer_plan(session, user_prompt, language)
            return plan
