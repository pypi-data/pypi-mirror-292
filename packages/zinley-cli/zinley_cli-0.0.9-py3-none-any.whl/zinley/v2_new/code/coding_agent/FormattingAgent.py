import os
import aiohttp
import asyncio
import json
import sys

class FormattingAgent:
    def __init__(self, role, directory_path, api_key, endpoint, deployment_id, max_tokens):
        """
        Initialize the FormattingAgent with directory path, API key, endpoint, deployment ID, and max tokens for API requests.

        Args:
            directory_path (str): Path to the directory containing .txt files.
            api_key (str): API key for Azure OpenAI API.
            endpoint (str): Endpoint for the Azure OpenAI API.
            deployment_id (str): Deployment ID for the model.
            max_tokens (int): Maximum tokens for the Azure OpenAI API response.
        """
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

    def initial_setup(self, user_prompt):
        """
        Initialize the conversation with a prompt for the assistant.

        Args:
            user_prompt (str): The user's prompt to initiate the conversation.
        """
        prompt = (
            f"You are a senior {self.role} and formatter agent. The current file code is disorganized; reformat it without changing function names, class names, structure, or any features. Ensure the functionality remains the same. Write detailed comments or notices for each function, class, and snippet. Respond with only the reformatted code for the file. Do not remove the file's default information at the top. Respond with only valid code without additional text or Markdown symbols."
        )

        self.conversation_history.append({"role": "system", "content": prompt})
        self.conversation_history.append({"role": "user", "content": f"Cool, this is user request: {user_prompt}"})
        self.conversation_history.append({"role": "assistant", "content": "Got it! I will follow exactly and respond only with plain code without additional text or Markdown symbols."})

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

    async def get_format(self, session, file):
        """
        Request code reformatting from Azure OpenAI API for a given file.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            file (str): Path to the file to be reformatted.

        Returns:
            str: Reformatted code or error reason.
        """
        file_content = self.read_file_content(file)
        if file_content:
            # Prepare payload for the API request
            prompt = f"Now work on this file: {file_content}"

            self.conversation_history.append({"role": "user", "content": prompt})

            payload = {
                "messages": self.conversation_history,
                "temperature": 0.2,
                "top_p": 0.1,
                "max_tokens": self.max_tokens
            }

            url = f"{self.endpoint}/openai/deployments/{self.deployment_id}/chat/completions?api-version=2024-04-01-preview"

            # Make an async POST request to Azure OpenAI API
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
                    return message_content
                else:
                    return None

    async def replace_all_code_in_file(self, file_path, new_code_snippet):
        """
        Replace the entire content of a file with the new code snippet.

        Args:
            file_path (str): Path to the file.
            new_code_snippet (str): New code to replace the current content.
        """
        try:
            with open(file_path, 'w') as file:
                file.write(new_code_snippet)
            print(f"All code formatted successfully in {file_path}.")
        except Exception as e:
            print(f"Error formatting code. Error: {e}")

    async def get_formats(self, files, prompt):
        """
        Format the content of all provided files using Azure OpenAI API.

        Args:
            files (list): List of file paths to be formatted.
            prompt (str): The user's prompt to initiate the formatting request.
        """
        # Step to remove all empty files from the list
        files = [file for file in files if file]
        
        file_paths = self.scan_needed_files(files)
        self.initial_setup(prompt)
        async with aiohttp.ClientSession() as session:
            for file in file_paths:
                code = await self.get_format(session, file)
                if code:
                    await self.replace_all_code_in_file(file, code)
                    print(f"Completed formatting for: {file}")
