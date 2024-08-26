import os
import aiohttp
import asyncio
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import clean_json

class IdeaDevelopment:
    def __init__(self, role, directory_path, api_key, endpoint, deployment_id, max_tokens):
        """
        Initialize the IdeaDevelopment agent with directory path, API key, endpoint, deployment ID, and max tokens for API requests.

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
        self.role = role
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.conversation_history = []

    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def initial_setup(self, files):
        """
        Initialize the conversation with a system prompt and user context.
        """

        all_file_contents = ""

        for file_path in files:
            file_content = self.read_file_content(file_path)
            if file_content:
                all_file_contents += f"\n\nFile: {file_path}:\n{file_content}"


        system_prompt = (
            f"You are a senior {self.role}. Analyze the provided project files and create a detailed core purely technical development and feature plan to achieve the user request that fits with the current project setup. Focus on the following:\n\n"

            # Section 1: Requirements Analysis
            "1. **Requirements Analysis:**\n"

            "1.1 **Existing Files:**\n"
            "- Identify existing files to work on and explain why they are needed.\n"
            "- Describe exactly what needs to be updated in these files.\n"
            "- Determine if they need to work with any other files for integration.\n\n"
            "- A paragraph detail description of what to be implemented.\n\n"

            "1.2 **New Files:**\n"
            "- Identify new files that need to be created and explain why they are needed.\n"
            "- Describe exactly what needs to be built in these new files.\n"
            "- Determine if they need to work with any other files for integration.\n"
            "- All new file names must be detailed and show specific usage to prevent future conflicts or overlapping.\n\n"
            "- A paragraph detail description of what to be implemented.\n\n"

            "1.3 **File Organization:**\n"
            "- Structure all new files and folders in a logical, senior-level manner; avoid putting everything together.\n"
            "- Always add/organize new files to a right folders, don't add all together."
            "- For all new files to be created, describe in detail the a new tree structure will be setup.\n"
            "- For each working file, list all related files that need to work together to provide enough context and prevent redeclaration or conflicts.\n\n"

            "1.4 **Best Practices:**\n"
            "- Follow best coding practices by using as many files as needed for specific purposes, aiming for clean code.\n"
            "- Never renaming existing files; only modify the content inside. If a file cannot be re-used, create a new file.\n"
            "- Specify the algorithms and tech stack to be implemented in each file, if necessary.\n"
            "- Describe what actions need to be performed in each specific file for this stage.\n\n"
            "- For all local image related tasks, set a placeholder and tell user to name the image exactly that name for auto showup.\n\n"
            "- For network images, using image link provide by user.\n\n"

            # Section 2: UX Workflow
            "2. **UX Workflow:**\n"
            "- Define UX Flow comprehensively.\n\n"

            # Section 3: System Design
            "3. **System Design:**\n"
            "- Provide a detailed and clear system design without writing code.\n\n"

            # Exclusions
            "Capabilities that you don’t have right now, ignore these related tasks:\n"
            "- Third party integration/installation\n"
            "- Create Core data\n"
            "- Install Networking dependencies like Firebase, AWS\n"
            "- Create new Test file\n"
            "- Can't add new images, using existing local images"
            "- Can't add new sounds, using existing local sounds"
        )


        self.conversation_history.append({"role": "system", "content": system_prompt})
        self.conversation_history.append({"role": "user", "content":  f"Here are the current project files:\n{all_file_contents}\n"})
        self.conversation_history.append({"role": "assistant", "content": "Got it! Give me user prompt so i can support them."})


    def scan_txt_files(self):
        """
        Scan for all txt files in the specified directory.

        Returns:
            list: Paths to all txt files.
        """
        txt_files = []

        if not os.path.exists(self.directory_path):
            print(f"Directory does not exist: {self.directory_path}")
            return txt_files

        for root, _, files in os.walk(self.directory_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    txt_files.append(file_path)

        return txt_files

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

    async def get_idea_plan(self, session, user_prompt):
        """
        Get development plan for all txt files from Azure OpenAI based on user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """
        prompt = (
             f"Follow the user prompt strictly and provide a no code response:\n{user_prompt}\n\n"
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

            plan = await response.json()

            if 'choices' in plan and len(plan['choices']) > 0:
                message_content = plan['choices'][0]['message']['content']
                self.conversation_history.append({"role": "assistant", "content": message_content})
                return message_content

    async def get_feedback_plan(self, session, user_prompt):
        """
        Get feedback plan for modifying the development plan based on user feedback.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            user_prompt (str): The user's feedback prompt.

        Returns:
            dict: Modified development plan or error reason.
        """
        prompt = (
             f"Follow the user feedback strictly to modify and provide a no code response:\n{user_prompt}\n\n"
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

            plan = await response.json()

            if 'choices' in plan and len(plan['choices']) > 0:
                message_content = plan['choices'][0]['message']['content']
                self.conversation_history.append({"role": "assistant", "content": message_content})
                return message_content

    async def get_idea_plans(self, user_prompt):
        """
        Get development plans for a list of txt files from Azure OpenAI based on user prompt.

        Args:
            files (list): List of file paths.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """

        async with aiohttp.ClientSession() as session:
            plan = await self.get_idea_plan(session, user_prompt)
            return plan

    async def get_feedback_plans(self, user_prompt):
        """
        Get feedback plans for modifying the development plan based on user feedback.

        Args:
            user_prompt (str): The user's feedback prompt.

        Returns:
            dict: Modified development plan or error reason.
        """
        async with aiohttp.ClientSession() as session:
            plan = await self.get_feedback_plan(session, user_prompt)
            return plan
