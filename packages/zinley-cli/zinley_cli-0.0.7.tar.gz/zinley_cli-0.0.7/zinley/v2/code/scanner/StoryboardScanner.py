import os
import aiohttp
import asyncio
import json

from json_repair import repair_json
from zinley.v2.code.log.logger_config import get_logger
logger = get_logger(__name__)

class StoryboardScanner:
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

    def scan_files_in_project(self):
        """
        Scan for all storyboard files in the project directory, excluding third-party directories like 'Pods'.

        Returns:
            list: Paths to all storyboard files.
        """
        storyboard_files = []

        for root, dirs, files in os.walk(self.project_path):
            if 'Pods' in root:
                continue
            for file in files:
                if file.endswith('.storyboard'):
                    file_path = os.path.join(root, file)
                    storyboard_files.append(file_path)

        return storyboard_files

    def read_file_content(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            logger.info(f"Failed to read file {file_path}: {e}")
            return None

    async def get_file_summary(self, session, file_path, file_content):
        """
        Get summary for a single storyboard file from Azure OpenAI.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            file_path (str): The path to the storyboard file.
            file_content (str): The content of the storyboard file.

        Returns:
            dict: Summary of the file or error reason.
        """
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a senior iOS developer. Analyze this storyboard file from an Xcode project. The file name is "
                        f"{os.path.basename(file_path)}. Provide only a JSON response without any additional text or Markdown formatting. "
                        "The JSON should be in the following format: {\"Purpose\": \"<short description>\", \"Key_features\": \"<key features>\", "
                        "\"All_scenes\": [{\"name\": \"<scene name>\", \"description\": \"<short description>\"}], "
                        "\"All_segue\": [{\"name\": \"<segue name>\", \"description\": \"<short description>\"}], "
                        "\"Notice_on_using\": \"<any special notes on using this file, potential bug, performance issue, please list everything!>\"}. Do not include any Markdown such as ```json or text outside of "
                        "the JSON structure and ensure precisely JSON format that not to cause fail to decode JSON response."
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

                try:
                    summary_json = json.loads(message_content)
                    return {
                        "file_path": file_path,
                        "summary": summary_json
                    }
                except json.JSONDecodeError:
                    good_json_string = repair_json(message_content)
                    plan_json = json.loads(good_json_string)
                    return {
                        "file_path": file_path,
                        "summary": plan_json
                    }

    async def get_file_summaries(self, files):
        """
        Get summaries for a list of storyboard files from Azure OpenAI.

        Args:
            files (list): List of file paths.

        Returns:
            list: List of dictionaries containing file summaries.
        """
        file_summaries = []

        async with aiohttp.ClientSession() as session:
            for file_path in files:
                try:
                    file_content = self.read_file_content(file_path)

                    if not file_content:
                        file_summaries.append({
                            "file_path": file_path,
                            "reason": "Failed to read file content"
                        })
                        continue

                    summary = await self.get_file_summary(session, file_path, file_content)
                    file_summaries.append(summary)

                except Exception as e:
                    file_summaries.append({
                        "file_path": file_path,
                        "reason": str(e)
                    })

        return file_summaries

    async def reprocess_failed_files(self, failed_files):
        """
        Reprocess files that failed to decode JSON response.

        Args:
            failed_files (list): List of failed file summaries.

        Returns:
            list: List of corrected file summaries.
        """
        async with aiohttp.ClientSession() as session:
            for failed_file in failed_files:
                file_path = failed_file["file_path"]
                raw_response = failed_file["raw_response"]

                try:
                    payload = {
                        "messages": [
                            {
                                "role": "user",
                                "content": f"The following JSON response could not be decoded. Please correct the JSON format and return only the corrected JSON: {raw_response}"
                            }
                        ],
                        "max_tokens": self.max_tokens
                    }

                    url = f"{self.endpoint}/openai/deployments/{self.deployment_id}/chat/completions?api-version=2024-04-01-preview"

                    async with session.post(url, headers=self.headers, json=payload) as response:
                        if response.status != 200:
                            response_json = await response.json()
                            error_message = response_json.get('error', {}).get('message', 'Unknown error')
                            failed_file["reason"] = error_message
                            continue

                        summary = await response.json()

                        if 'choices' in summary and len(summary['choices']) > 0:
                            message_content = summary['choices'][0]['message']['content']

                            try:
                                summary_json = json.loads(message_content)
                                failed_file["summary"] = summary_json
                                failed_file.pop("reason", None)
                                failed_file.pop("raw_response", None)
                            except json.JSONDecodeError:
                                logger.info(f"Failed to decode JSON response for file {file_path}. Response content: {message_content}")
                                failed_file["reason"] = "Failed to decode JSON response again"
                                failed_file["raw_response"] = message_content

                except Exception as e:
                    failed_file["reason"] = str(e)

        return failed_files
