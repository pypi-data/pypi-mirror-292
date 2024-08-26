import os
import aiohttp
import asyncio
import json

class ScannerAgent:
    def __init__(self, project_path, api_key, endpoint, deployment_id, max_tokens):
        self.project_path = project_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }


    def read_file_content(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return None

    def scan_for_single_file(self, filename):
        """
        Scan for a single specified file in the specified directory.

        Args:
            filename (str): The name of the file to look for.

        Returns:
            str: Path to the specified file if found, else None.
        """
        if not os.path.exists(self.project_path):
            print(f"Directory does not exist: {self.project_path}")
            return None

        for root, _, files in os.walk(self.project_path):
            if filename in files:
                return os.path.join(root, filename)

        print(f"Coudn't find file {filename} in {self.project_path}")
        return None

    async def get_file_summary(self, session, file_path, file_content):
        """
        Get summary for a single Swift file from Azure OpenAI.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            file_path (str): The path to the Swift file.
            file_content (str): The content of the Swift file.

        Returns:
            dict: Summary of the file or error reason.
        """
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Analyze this file comprehensively. The file name is "
                        f"{os.path.basename(file_path)}. "
                        "0. If file is empty, just put empty file, ignore all the below\n"
                        "If file is not empty, provide a brief summary including:\n"
                        "1. Purpose: Short description of the file's purpose.\n"
                        "2. Key Features: Key features of the file.\n"
                        "3. Classes (Don't mention if not applicable): Name and short description of each class and usage.\n"
                        "4. Functions (Don't mention if not applicable): Name and short description of each function and usage.\n"
                        "5. Related Files (Don't mention if not applicable): Names of all possible related files how it is used.\n"
                        "6. Potential Issues (Don't mention if not applicable): Possible memory leaks, UI rendering issues, or potential bugs.\n"
                        "Keep the response as short as possible."
                    )
                },
                {
                    "role": "user",
                    "content": file_content
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": 0.2,
            "top_p": 0.1
        }

        url = f"{self.endpoint}/openai/deployments/{self.deployment_id}/chat/completions?api-version=2024-04-01-preview"

        async with session.post(url, headers=self.headers, json=payload) as response:
            if response.status != 200:
                response_json = await response.json()
                error_message = response_json.get('error', {}).get('message', 'Unknown error')
                return {
                    "file_path": file_path,
                    "reason": error_message
                }

            summary = await response.json()

            if 'choices' in summary and len(summary['choices']) > 0:
                message_content = summary['choices'][0]['message']['content']
                return message_content


    async def get_file_summaries(self, file):
        """
        Get summaries for a list of Swift files from Azure OpenAI.

        Args:
            files (list): List of file paths.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        file_summaries = []
        file_path = self.scan_for_single_file(file)
        if file_path != None:
            async with aiohttp.ClientSession() as session:
                try:
                    file_content = self.read_file_content(file_path)

                    if file_content:
                        summary = await self.get_file_summary(session, file_path, file_content)
                        file_summaries.append({
                            "file_path": file_path,
                            "summary": f"{summary}"
                        })
                        file_summaries.append(summary)

                except Exception as e:
                    print(e)


            return file_summaries
