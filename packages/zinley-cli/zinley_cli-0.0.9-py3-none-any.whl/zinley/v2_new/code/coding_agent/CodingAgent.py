import os
import sys
import asyncio
from datetime import datetime
import aiohttp
import json
import re
from json_repair import repair_json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import get_current_time_formatted, clean_json

class CodingAgent:
    def __init__(self, role, directory_path, api_key, endpoint, deployment_id, max_tokens):
        self.directory_path = directory_path
        self.api_key = api_key
        self.role = role
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.conversation_history = []

    def get_current_time_formatted(self):
        """Return the current time formatted as mm/dd/yy."""
        current_time = datetime.now()
        formatted_time = current_time.strftime("%m/%d/%y")
        return formatted_time

    def initial_setup(self, instructions, context):
        """Initialize the setup with the provided instructions and context."""

        scope_explanation = (
            "file_name: Return the name of the current working file. Every time I prompt back, only work on one single file please.\n"
            "Purpose_detail: Return the 1 to 2 sentence about what you are doing.\n"
            "code: Return the full code for this specific file.\n"
            f"If this is a new file, update {self.get_current_time_formatted()} on the file description.\n"
            "Is_completed: return either true/false to indicate if this is the last step for the whole milestone. No further steps should be done and it shouldn't prompt back to you.\n"
        )


        prompt = (
            f"You are a senior {self.role} working as a coding agent. You will receive detailed instructions to work on. "
            "Respond with JSON format specifying what to work on each specific file based on the provided instructions.\n\n"
            "Your code must always be:\n"
            "- Clean and comprehensive, demonstrating senior-level expertise.\n"
            "- Include detailed comments or notices for each function, class, and snippet.\n"
            "- Adhere to safety and error-catching practices to prevent crashes.\n"
            "- Ensure UI rendering is not done on the main thread.\n"
            "- Avoid reference cycles to ensure proper memory management using weak and unowned references appropriately.\n"
            "{\n"
            "    \"Is_Completed\": \"True/False\",\n"
            "    \"Title\": \"Implementing login functionality\",\n"
            "    \"Purpose_detail\": \"Create a login screen for user authentication.\",\n"
            "    \"file_name\": \"LoginViewController.swift\",\n"
            "    \"code\": \"func addNumbers(a: Int, b: Int) -> Int {\\n    return a + b\\n}\"\n"
            "}\n"
            f"Explanation and rules: {scope_explanation}"
            "Always keep the file default description as as original.\n"
            "Return only a valid JSON response without additional text, Markdown symbols, or invalid escapes."
        )

        self.conversation_history.append({"role": "system", "content": prompt})
        self.conversation_history.append({"role": "user", "content": f"These are your instructions: {instructions} and the current context: {context}"})
        self.conversation_history.append({"role": "assistant", "content": "Got it! I will follow exactly to achieve this."})


    def scan_for_single_file(self, filename):
        """
        Scan for a single specified file in the specified directory.

        Args:
            filename (str): The name of the file to look for.

        Returns:
            str: Path to the specified file if found, else None.
        """
        if not os.path.exists(self.directory_path):
            print(f"Directory does not exist: {self.directory_path}")
            return None

        for root, _, files in os.walk(self.directory_path):
            if filename in files:
                return os.path.join(root, filename)

        return None

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
        """
        Read and return the content of the specified file.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: Content of the file.
        """
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return None

    async def get_coding_request(self, session, is_first, title):
        """
        Get coding response for the given instruction and context from Azure OpenAI.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            is_first (bool): Flag to indicate if it's the first request.
            title (str): Title of the coding task.

        Returns:
            dict: The code response or error reason.
        """
        # Update conversation history
        if is_first:
            prompt = "Get started with the first file, return the next file with exact responding example. If there are no next files to be implemented, just return with Mark Is_Completed with True, otherwise keep it False."
        else:
            prompt = f"{title} is done: Same the next file. If there are no next files to be implemented, just return with Mark Is_Completed with True, otherwise keep it False."

        self.conversation_history.append({"role": "user", "content": prompt})

        payload = {
            "messages": self.conversation_history,
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

            code = await response.json()

            if 'choices' in code and len(code['choices']) > 0:
                message_content = code['choices'][0]['message']['content']
                self.conversation_history.append({"role": "assistant", "content": message_content})
                try:
                    plan_json = json.loads(message_content)
                    return plan_json
                except json.JSONDecodeError:
                    good_json_string = repair_json(message_content)
                    plan_json = json.loads(good_json_string)
                    return plan_json

    async def get_coding_requests(self, is_first, title):
        """
        Get coding responses for a list of files from Azure OpenAI based on user instruction.

        Args:
            is_first (bool): Flag to indicate if it's the first request.
            title (str): Title of the coding task.

        Returns:
            dict: The code response or error reason.
        """
        async with aiohttp.ClientSession() as session:
            return await self.get_coding_request(session, is_first, title)

    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
