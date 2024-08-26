import os
import aiohttp
import asyncio
import json
import sys
from json_repair import repair_json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import clean_json

class FileManagerAgent:
    def __init__(self, directory_path, api_key, endpoint, deployment_id, max_tokens):
        """
        Initialize the FileManagerAgent with directory path, API key, endpoint, deployment ID, and max tokens for API requests.

        Args:
            directory_path (str): Path to the directory containing .txt files.
            api_key (str): API key for Azure OpenAI API.
            endpoint (str): Endpoint URL for Azure OpenAI.
            deployment_id (str): Deployment ID for the model.
            max_tokens (int): Maximum tokens for the Azure OpenAI API response.
        """
        self.directory_path = directory_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def read_file_content(self, file_path):
        """
        Read the content of a file.

        Args:
            file_path (str): Path to the file to read.

        Returns:
            str: Content of the file, or None if an error occurs.
        """
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return None

    async def get_file_planning(self, session, idea, tree):
        """
        Request file planning from Azure OpenAI API for a given idea and project structure.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            idea (str): The general plan idea.
            tree (str): The project structure.

        Returns:
            dict: JSON response with the plan.
        """
        prompt = (
            "From the provided development plan, build a JSON to add all new files to be created and list all Existing_files to be used. Provide only a JSON response without any additional text or Markdown formatting. "
            "Adding_new_files must include all new files that need to be created. "
            "Existing_files must include all existing files name only, not the whole path that need to be used. "
            "If no file needs to be created, follow this JSON format: "
            "{\n"
            "    \"Is_creating\": false,\n"
            "    \"Existing_files\": [file1.swift, file2.m, file3.h]\n"
            "    \"Adding_new_files\": []\n"
            "}\n\n"
            "If there are files that will need to be created, follow this JSON format: "
            "{\n"
            "    \"Is_creating\": true,\n"
            "    \"Existing_files\": [file1.swift, file2.m, file3.h]\n"
            "    \"Adding_new_files\": [\n"
            "        {\n"
            "            \"Title\": \"Creating a new Swift file\",\n"
            "            \"Function_to_call\": \"create_and_add_file_to_xcodeproj\",\n"
            "            \"Parameters\": {\n"
            "                \"project_root_path\": \"" + self.directory_path + "\",\n"
            "                \"relative_path\": \"Current project main folder name\",\n"
            "                \"file_name\": \"example.swift\"\n"
            "            }\n"
            "        }\n"
            "    ]\n"
            "}\n\n"
            "Existing_files include only single file name instead of the whole path.\n"
            "relative_path must not overlap with project_root_path, must only show new path.\n"
            "Return only valid JSON without Markdown symbols or invalid escapes."
        )

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": f"This is the development plan:\n{idea}\nThis is the current project structure:\n{tree}\n"
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
                print(f"Error: {error_message}")
                return {
                    "reason": error_message
                }

            plan = await response.json()

            if 'choices' in plan and len(plan['choices']) > 0:
                message_content = plan['choices'][0]['message']['content']
                try:
                    plan_json = json.loads(message_content)
                    return plan_json
                except json.JSONDecodeError:
                    good_json_string = repair_json(message_content)
                    plan_json = json.loads(good_json_string)
                    return plan_json

    async def get_adding_file_planning(self, session, idea, tree):
        """
        Request file planning from Azure OpenAI API for a given idea and project structure.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            idea (str): The general plan idea.
            tree (str): The project structure.

        Returns:
            dict: JSON response with the plan.
        """
        prompt = (
            "From the provided development plan, build a JSON to add all new files to be created. Provide only a JSON response without any additional text or Markdown formatting. "
            "Adding_new_files must include all new files that need to be created. "
            "If there are files that will need to be created, follow this JSON format: "
            "{\n"
            "    \"Is_creating\": true,\n"
            "    \"Adding_new_files\": [\n"
            "        {\n"
            "            \"Title\": \"Creating a new Swift file\",\n"
            "            \"Function_to_call\": \"create_and_add_file_to_xcodeproj\",\n"
            "            \"Parameters\": {\n"
            "                \"project_root_path\": \"" + self.directory_path + "\",\n"
            "                \"relative_path\": \"Current project main folder name\",\n"
            "                \"file_name\": \"example.swift\"\n"
            "            }\n"
            "        }\n"
            "    ]\n"
            "}\n\n"
            "If there are folders only that will need to be created, mark file_name = empty string "
            "relative_path must not overlap with project_root_path, must only show new path.\n"
            "Return only valid JSON without Markdown symbols or invalid escapes."
        )

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": f"This is the development plan:\n{idea}\nThis is the current project structure:\n{tree}\n"
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
                print(f"Error: {error_message}")
                return {
                    "reason": error_message
                }

            plan = await response.json()

            if 'choices' in plan and len(plan['choices']) > 0:
                message_content = plan['choices'][0]['message']['content']
                try:
                    plan_json = json.loads(message_content)
                    return plan_json
                except json.JSONDecodeError:
                    good_json_string = repair_json(message_content)
                    plan_json = json.loads(good_json_string)
                    return plan_json


    async def get_moving_file_planning(self, session, idea, tree):
        """
        Request file planning from Azure OpenAI API for a given idea and project structure.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            idea (str): The general plan idea.
            tree (str): The project structure.

        Returns:
            dict: JSON response with the plan.
        """
        prompt = (
            "From the provided development plan, build a JSON to move file. Provide only a JSON response without any additional text or Markdown formatting. "
            "Moving_files must include all new files that need to be moved. "
            "If there are files that will need to be moved, follow this JSON format: "
            "{\n"
            "    \"Is_moving\": true,\n"
            "    \"Moving_new_files\": [\n"
            "        {\n"
            "            \"Title\": \"Moving a Swift file\",\n"
            "            \"Function_to_call\": \"move_file_within_xcodeproj\",\n"
            "            \"Parameters\": {\n"
            "                \"new_project_root_path\": \"" + self.directory_path + "\",\n"
            "                \"new_relative_path\": \"New project main folder name\",\n"
            "                \"file_name\": \"example.swift\"\n"
            "            }\n"
            "        }\n"
            "    ]\n"
            "}\n\n"
            "If there are folders only that will need to be created, mark file_name = empty string "
            "relative_path must not overlap with project_root_path, must only show new path.\n"
            "Return only valid JSON without Markdown symbols or invalid escapes."
        )

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": f"This is the development plan:\n{idea}\nThis is the current project structure:\n{tree}\n"
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
                print(f"Error: {error_message}")
                return {
                    "reason": error_message
                }

            plan = await response.json()

            if 'choices' in plan and len(plan['choices']) > 0:
                message_content = plan['choices'][0]['message']['content']
                try:
                    plan_json = json.loads(message_content)
                    return plan_json
                except json.JSONDecodeError:
                    good_json_string = repair_json(message_content)
                    plan_json = json.loads(good_json_string)
                    return plan_json

    async def get_moving_file_plannings(self, idea, tree):
        """
        Request file planning from Azure OpenAI API for a given idea and project structure.

        Args:
            idea (str): The general plan idea.
            tree (list): List of file paths representing the project structure.

        Returns:
            dict: JSON response with the plan.
        """
        async with aiohttp.ClientSession() as session:
            all_file_contents = ""

            for file_path in tree:
                file_content = self.read_file_content(file_path)
                if file_content:
                    all_file_contents += f"\n\nFile: {file_path}\n{file_content}"

            plan = await self.get_moving_file_planning(session, idea, all_file_contents)
            return plan

    async def get_adding_file_plannings(self, idea, tree):
        """
        Request file planning from Azure OpenAI API for a given idea and project structure.

        Args:
            idea (str): The general plan idea.
            tree (list): List of file paths representing the project structure.

        Returns:
            dict: JSON response with the plan.
        """
        async with aiohttp.ClientSession() as session:
            all_file_contents = ""

            for file_path in tree:
                file_content = self.read_file_content(file_path)
                if file_content:
                    all_file_contents += f"\n\nFile: {file_path}\n{file_content}"

            plan = await self.get_adding_file_planning(session, idea, all_file_contents)
            return plan

    async def get_file_plannings(self, idea, tree):
        """
        Request file planning from Azure OpenAI API for a given idea and project structure.

        Args:
            idea (str): The general plan idea.
            tree (list): List of file paths representing the project structure.

        Returns:
            dict: JSON response with the plan.
        """
        async with aiohttp.ClientSession() as session:
            all_file_contents = ""

            for file_path in tree:
                file_content = self.read_file_content(file_path)
                if file_content:
                    all_file_contents += f"\n\nFile: {file_path}\n{file_content}"

            plan = await self.get_file_planning(session, idea, all_file_contents)
            return plan
