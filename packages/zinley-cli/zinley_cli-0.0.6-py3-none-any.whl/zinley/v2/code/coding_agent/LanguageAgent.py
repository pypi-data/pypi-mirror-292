import os
import aiohttp
import asyncio
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import clean_json
from json_repair import repair_json

class LanguageAgent:
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

    async def get_language_plan(self, session, user_prompt, role):
        """
        Get a development plan for the given prompt from Azure OpenAI.

        Args:
            role: role getting from coding controller
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
                        f"You are a senior {role} and prompt engineering specialist. "
                        "If the user's original prompt is not in English, translate it to 100% English. "
                        "Correct grammar, ensure it is clear and concise. Keep it crisp and short, avoiding confusion."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"User original prompt:\n{user_prompt}\n\n"
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

    async def get_language_plans(self, user_prompt, role):
        """
        Get development plans based on the user prompt.

        Args:
            role: getting from coding controller
            user_prompt (str): The user's prompt.

        Returns:
            str: Development plan or error reason.
        """
        async with aiohttp.ClientSession() as session:
            plan = await self.get_language_plan(session, user_prompt, role)
            return plan
