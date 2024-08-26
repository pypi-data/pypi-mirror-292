import os
import sys
import asyncio
import re
from json_repair import repair_json
import aiohttp
import json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import get_current_time_formatted, clean_json

class BugExplainer:
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
        self.conversation_history = []

    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def initial_setup(self):
        """Set up the initial prompt for the bug-fixing agent."""
        prompt = (
            f"You are a senior {self.role} working as a bug-fixing agent. Analyze the provided project context and current errors, and provide detailed steps to fix the project in a structured manner. "
            "Sometime even bugs are in multiple files but cause by one file, find the root cause to fix instead of fixing all files. "
            "Enforce the following rules: "
            "(1) Each step must involve a single file only. \n"
            "(2) list_related_file_name must have list only all the possible files name that may cause damage to this working file, otherwise just return empty. \n"
            "(3) is_new is for if this file need to be newly created. Sometime file is missing or maybe deleted accidentally, try to restore file as best as possible with provided context, and mark is_new is True, otherwise is_new must be False. \n"
            "(4) new_file_location is for the location of file if this file need to be newly created. Describe any relative path and folder where the new file will be created if needed. \n"
            "The JSON response must follow strictly this format:\n\n"
            "{\n"
            "    \"steps\": [\n"
            "        {\n"
            "            \"Step\": 1,\n"
            "            \"Title\": \"Implementing login functionality\",\n"
            "            \"file_name\": \"LoginViewController.swift\",\n"
            "            \"is_new\": \"True/False\",\n"
            "            \"new_file_location\": \"Relative/Path/To/Folder\",\n"
            "            \"list_related_file_name\": [\"LoginViewController.swift\", \"AnotherFile.swift\"],\n"
            "            \"Solution_detail_title\": \"Fixing a login screen for user authentication.\",\n"
            "            \"all_comprehensive_solutions_for_each_bugs\": \"Detailed descriptions and explanation step by step on how to fix each problem and for each bug. (need to list exact scope of damaged code and how to fix)\"\n"
            "        }\n"
            "    ]\n"
            "}\n"
            "Don't add any additional beside example above."
            "Return only a valid JSON response without additional text or Markdown symbols or invalid escapes."
        )

        self.conversation_history.append({"role": "system", "content": prompt})

    def scan_needed_files(self, filenames):
        """
        Scan for specified files in the specified directory.

        Args:
            filenames (list): List of filenames to look for.

        Returns:
            list: Paths to the specified files if found.
        """
        found_files = []

        if not os.path.exists(self.directory_path):
            print(f"Directory does not exist: {self.directory_path}")
            return found_files

        for root, _, files in os.walk(self.directory_path):
            for filename in filenames:
                if filename in files:
                    file_path = os.path.join(root, filename)
                    found_files.append(file_path)
        return found_files

    def read_file_content(self, file_path):
        """Read and return the content of the specified file."""
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return None

    async def get_bugFixed_suggest_request(self, session, bug_log_path, all_file_contents, overview):
        """
        Get development plan for all txt files from Azure OpenAI based on user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            all_file_contents (str): The concatenated contents of all files.
            overview (str): Project overview description.

        Returns:
            dict: Development plan or error reason.
        """
        bug_logs = self.read_file_content(bug_log_path)
        if not bug_logs:
            return "Bug log file not found or empty."

        error_prompt = (
            f"Current working file:\n{all_file_contents}\n\n"
            f"Project overview:\n{overview}\n\n"
            f"Bug logs:\n{bug_logs}\n\n"
            "Return only a valid JSON bug fix response without additional text or Markdown symbols or invalid escapes.\n\n"
        ).replace("<project_directory>", self.directory_path)

        self.conversation_history.append({"role": "user", "content": error_prompt})

        payload = {
            "messages": self.conversation_history,
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

    async def get_bugFixed_suggest_requests(self, bug_log_path, files, overview):
        """
        Get development plans for a list of txt files from Azure OpenAI based on user prompt.

        Args:
            bug_log_path (str): Path to the bug log file.
            files (list): List of file paths.
            overview (str): Overview description.

        Returns:
            dict: Development plan or error reason.
        """
        # Step to remove all empty files from the list
        filtered_lists = [file for file in files if file]

        print(f"Scanning: {filtered_lists}")

        async with aiohttp.ClientSession() as session:
            all_file_contents = ""

            # Scan needed files based on the filtered list
            final_files_paths = self.scan_needed_files(filtered_lists)

            for file_path in final_files_paths:
                try:
                    file_content = self.read_file_content(file_path)
                    if file_content:
                        all_file_contents += f"\n\nFile: {file_path}\n{file_content}"
                except Exception as e:
                    all_file_contents += f"\n\nFailed to read file {file_path}: {str(e)}"

            # Get the bug-fixed suggestion request
            plan = await self.get_bugFixed_suggest_request(session, bug_log_path, all_file_contents, overview)
            return plan
