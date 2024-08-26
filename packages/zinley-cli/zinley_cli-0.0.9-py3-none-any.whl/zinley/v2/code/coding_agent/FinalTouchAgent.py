import os
import asyncio
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Scanner1.ProjectScanner1 import ProjectScanner1

class FinalTouchAgent:
    def __init__(self, directory_path, api_key, endpoint, deployment_id, max_tokens):
        """
        Initialize the FinalTouchAgent with directory path, API key, endpoint, deployment ID, and max tokens for API requests.

        Args:
            directory_path (str): Path to the project directory.
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
        self.scanner = ProjectScanner1(directory_path, api_key, endpoint, deployment_id, max_tokens)


    async def scanFiles(self, files):
        """
        Categorize and scan the specified files.

        Args:
            files (list): List of filenames to scan.

        Returns:
            None
        """
        print(f"Final step: {list(files)}")
        await self.scanner.scanning_files(list(files))
