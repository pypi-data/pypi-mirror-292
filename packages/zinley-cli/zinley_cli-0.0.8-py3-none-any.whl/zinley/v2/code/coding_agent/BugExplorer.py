
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
from zinley.v2.code.log.logger_config import get_logger
logger = get_logger(__name__)

class BugExplorer:
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
        self.conversation_history = []

    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def initial_setup(self, role):
        """Set up the initial prompt for the bug-fixing agent."""
        prompt = (
            "You are a senior software engineer working as a bug-scanner agent. Analyze the provided project context to find any potential errors (syntax errors, integration errors, performance errors, memory leaks, and all possible critical errors you can scan), and provide detailed steps to fix the project in a structured manner. "
            "Sometimes bugs are in multiple files but caused by one file; find the root cause to fix instead of fixing all files. "
            "Enforce the following rules: "
            "(0) If no potential bugs, return False for 'Has_Bugs'; otherwise, return True for 'Has_Bugs'. \n"
            "(1) file_name must include only single file name that need to be work on without any path. \n"
            "(2) Each step must involve a single file only. \n"
            "(3) 'list_related_file_name' must list only all the possible file names that may cause issues in the working file; otherwise, just return an empty list. \n"
            "(4) 'is_new' is used to indicate if a file needs to be newly created. If a file is missing or accidentally deleted, try to restore the file as best as possible with the provided context, and mark 'is_new' as True; otherwise, 'is_new' must be False. \n"
            "(5) 'new_file_location' is the location of the file if it needs to be newly created. Describe any relative path and folder where the new file will be created if needed. \n"
            "If there are no potential bugs, please strictly follow this format for the JSON response:\n\n"
            "{\n"
            "    \"Has_Bugs\": False,\n"
            "    \"steps\": []\n"
            "}\n"
            "If there are potential bugs, please strictly follow this format for the JSON response:\n\n"
            "{\n"
            "    \"Has_Bugs\": True,\n"
            "    \"steps\": [\n"
            "        {\n"
            "            \"Step\": 1,\n"
            "            \"file_name\": \"LoginViewController.extension\",\n"
            "            \"tech_stack\": \"Programming language used for this file\",\n"
            "            \"list_related_file_name\": [\"LoginViewController.extension\", \"AnotherFile.extension\"],\n"
            "            \"Solution_detail_title\": \"Fixing a login screen for user authentication.\",\n"
            "            \"all_comprehensive_solutions_for_each_bugs\": \"Detailed descriptions and explanation step by step on how to fix each problem and for each bug. (List the exact scope of damaged code and how to fix it)\"\n"
            "        }\n"
            "    ]\n"
            "}\n"
            "Return only a valid JSON response without any additional text."
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
            logger.debug(f"Failed to read file {file_path}: {e}")
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

        complile_bug_logs = self.read_file_content(bug_log_path)
        if not complile_bug_logs:
            error_prompt = (
                f"Current working file:\n{all_file_contents}\n\n"
                f"Project overview:\n{overview}\n\n"
                f"Bug logs:\n{complile_bug_logs}\n\n"
                "Return only a valid JSON bug exploring response without additional text or Markdown symbols or invalid escapes.\n\n"
            ).replace("<project_directory>", self.directory_path)
        else:
            error_prompt = (
                f"Current working file:\n{all_file_contents}\n\n"
                f"Project overview:\n{overview}\n\n"
                "Return only a valid JSON bug exploring response without additional text or Markdown symbols or invalid escapes.\n\n"
            ).replace("<project_directory>", self.directory_path)


        self.conversation_history.append({"role": "user", "content": error_prompt})

        payload = {
            "messages": self.conversation_history,
            "max_tokens": self.max_tokens,
            "temperature": 0.2,
            "top_p": 0.1
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
            files (list): List of file paths.
            overview (str): Overview description.

        Returns:
            dict: Development plan or error reason.
        """
        # Step to remove all empty files from the list
        filtered_lists = [os.path.basename(file) for file in files if file]

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
