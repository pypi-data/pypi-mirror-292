import os
import sys
import asyncio
import re
import aiohttp
import json
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import get_current_time_formatted, clean_json
from json_repair import repair_json

class SelfHealingAgent:

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

    def get_current_time_formatted(self):
        """Get the current time formatted as mm/dd/yy."""
        current_time = datetime.now()
        formatted_time = current_time.strftime("%m/%d/%y")
        return formatted_time

    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def initial_setup(self):
        """
        Initialize the conversation with a system prompt and user context.
        """
        prompt = (
            f"You are a senior {self.role} working as a fixing bug agent. You will receive detailed fixing bug instructions, current damaged file context and all current related files. Your need to work on a specific file to resolve bugs. "
            "Resolve problem without changing / impacting original features and functional "
            "Respond with new entirely full code for the current fixing file based on the provided fixing instructions.\n\n"
            "Your code must always be:\n"
            "- Clean and comprehensive, demonstrating senior-level expertise.\n"
            "- Include detailed comments or notices for each function, class, and snippet.\n"
            "- Adhere to safety and error-catching practices to prevent crashes.\n"
            "- Ensure UI rendering is not done on the main thread.\n"
            "- Avoid reference cycles to ensure proper memory management using weak and unowned references appropriately.\n"
            "Always keep the file default description as as original.\n"
            "Respond with only a valid code response without additional text, Markdown symbols."
        )

        self.conversation_history.append({"role": "system", "content": prompt})

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
        Read the content of a specified file.

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

    def read_all_file_content(self, all_path):
        """
        Read the content of all specified files.

        Args:
            all_path (list): List of file paths.

        Returns:
            str: Concatenated content of all files.
        """
        all_context = ""

        for path in all_path:
            file_context = self.read_file_content(path)
            all_context += f"\n\nFile: {path}\n{file_context}"

        return all_context

    async def get_fixing_request(self, session, instruction, file_content, all_file_content):
        """
        Get fixing response for the given instruction and context from Azure OpenAI.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            instruction (str): The fixing instructions.
            file_content (str): The content of the file to be fixed.
            all_file_content (str): The content of all related files.

        Returns:
            dict: Fixing response or error reason.
        """

        prompt = ""

        if all_file_content != "":
            prompt = (
                f"Current damaged file:\n{file_content}\n\n"
                f"Related files context:\n{all_file_content}\n\n"
                f"Follow this instructions:\n{instruction}\n\n"
                "Always keep the file default description as as original.\n"
                "Respond only plain code without additional text, Markdown symbols."
            )
        else:
            prompt = (
                f"Current damaged file:\n{file_content}\n\n"
                f"Follow this instructions:\n{instruction}\n\n"
                "Always keep the file default description as as original.\n"
                "Respond only plain code without additional text, Markdown symbols."
            )

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
                self.conversation_history.pop()
                return message_content

    async def get_fixing_requests(self, instructions):
        """
        Get fixing responses for a list of instructions from Azure OpenAI based on user prompt.

        Args:
            instructions (list): List of instructions for fixing bugs.

        Returns:
            dict: Fixing response or error reason.
        """
        for instruction in instructions:
            file_name = instruction['file_name']
            list_related_file_name = instruction['list_related_file_name']
            all_comprehensive_solutions_for_each_bugs = instruction['all_comprehensive_solutions_for_each_bugs']
            if file_name in list_related_file_name:
                list_related_file_name.remove(file_name)

            if len(list_related_file_name) == 0:
                main_path = self.scan_for_single_file(file_name)
                file_content = self.read_file_content(main_path)
                print(f"Working on: {instruction['Solution_detail_title']}")
                async with aiohttp.ClientSession() as session:
                    code = await self.get_fixing_request(session, all_comprehensive_solutions_for_each_bugs, file_content, "")
                    await self.replace_all_code_in_file(main_path, code)
                    print(f"Done tasks for: {instruction['Solution_detail_title']}")
            else:
                main_path = self.scan_for_single_file(file_name)
                all_path = self.scan_needed_files(list_related_file_name)
                file_content = self.read_file_content(main_path)
                all_file_content = self.read_all_file_content(all_path)
                print(f"Working on: {instruction['Solution_detail_title']}")
                async with aiohttp.ClientSession() as session:
                    code = await self.get_fixing_request(session, all_comprehensive_solutions_for_each_bugs, file_content, all_file_content)
                    await self.replace_all_code_in_file(main_path, code)
                    print(f"Done tasks for: {instruction['Solution_detail_title']}")

    async def replace_all_code_in_file(self, file_path, new_code_snippet):
        """
        Replace the entire content of a file with the new code snippet.

        Args:
            file_path (str): Path to the file.
            new_code_snippet (str): New code to replace the current content.
        """
        try:
            with open(file_path, 'w') as file:
                if self.contains_markdown_code(new_code_snippet):
                    cleaned_code = self.remove_markdown_code(new_code_snippet)
                    file.write(cleaned_code)
                else:
                    file.write(new_code_snippet)
            print(f"The codes have been fixed successfully written in... {file_path}.")
        except Exception as e:
            print(f"Error fixing code. Error: {e}")

    def contains_markdown_code(self, content):
        """
        Check if the content contains markdown code blocks.

        Args:
            content (str): The input string.

        Returns:
            bool: Boolean indicating if markdown code blocks are present.
        """
        markdown_code_pattern = r'```[\w]*[\s\S]*?```'
        return bool(re.search(markdown_code_pattern, content, re.MULTILINE))

    def remove_markdown_code(self, content):
        """
        Remove the first and last lines if they are markdown code block delimiters.

        Args:
            content (str): The input string containing markdown code blocks.

        Returns:
            str: A string with the markdown code block delimiters removed.
        """
        lines = content.splitlines()

        if lines and lines[0].startswith('```') and lines[-1].startswith('```'):
            lines = lines[1:-1]

        return '\n'.join(lines).strip()
