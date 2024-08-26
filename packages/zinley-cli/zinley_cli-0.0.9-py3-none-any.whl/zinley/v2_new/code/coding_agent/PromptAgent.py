import os
import aiohttp
import asyncio
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import clean_json
from json_repair import repair_json

class PromptAgent:
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

    def initial_setup(self, files, user_prompt):
        """
        Initialize the conversation with a system prompt and user context.
        """
        system_prompt = (
            f"You are a senior {self.role} and prompt engineering specialist. Analyze the provided project files and the user's prompt. Brainstorm additional potential features and requirements based on the user's prompt and develop a comprehensive high-level milestone. Split them into milestone development plans for the technical team. Follow these guidelines:\n\n"
            "- Each milestone must cover a broad area, such as setting up the project structure, adding more comprehensive features with specific requirements, and more.\n"
            "- The implementation_prompt must be a paragraph and must follow these rules:\n"
            "  - Must be comprehensive enough for developer team know what to build exactly without having to guess.\n"
            "  - If tasks are related to UI, develop comprehensive UI/UX requirements.\n"
            "  - Set clear goals and objectives.\n"
            "  - Provide context and background information.\n"
            "- Goal must be a single sentence about what to build and focus in this stage:\n"
            "The JSON response must follow this format:\n\n"
            "{\n"
            "    \"milestones\": [\n"
            "        {\n"
            "            \"milestone\": 1,\n"
            "            \"Goal\": \"Improve login functionality\",\n"
            "            \"implementation_prompt\": \"\"\n"
            "        }\n"
            "    ]\n"
            "}\n"
            "Capabilities that you don’t have right now, ignore these related tasks:\n"
            "- Third-party integration.\n"
            "- Core Data.\n"
            "- Networking dependencies like Firebase, AWS.\n"
            "- Test file related tasks.\n"
            "- Refinement and Bug Fixes.\n"
            "- Optimize Application for Performance and Accessibility.\n"
            "- Audit.\n"
            "Return only a valid JSON response without additional text or Markdown symbols."
        )

        all_file_contents = ""

        for file_path in files:
            file_content = self.read_file_content(file_path)
            if file_content:
                all_file_contents += f"\n\nFile: {file_path}:\n{file_content}"


        self.conversation_history.append({"role": "system", "content": system_prompt})
        self.conversation_history.append({"role": "assistant", "content": "Got it! I will follow exactly to achieve this."})
        self.conversation_history.append({"role": "system", "content": f"Here are the current project files:\n{all_file_contents}"})
        self.conversation_history.append({"role": "assistant", "content": "Got it! I will analysis current project context overview carefully."})

    def clear_conversation_history(self):
        """Clear the conversation and feedback history."""
        self.conversation_history = []

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
        Read the content of a specified file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The content of the file, or None if an error occurs.
        """
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return None

    async def get_prompt_plan(self, session, user_prompt):
        """
        Get a detailed prompt plan for all txt files from Azure OpenAI based on the user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            all_file_contents (str): The concatenated contents of all files.
            user_prompt (str): The user's prompt.

        Returns:
            str: Detailed prompt or error reason.
        """

        prompt = f"User prompt: {user_prompt}\n\n"

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
                try:
                    plan_json = json.loads(message_content)
                    return plan_json
                except json.JSONDecodeError:
                    good_json_string = repair_json(message_content)
                    plan_json = json.loads(good_json_string)
                    return plan_json

    async def get_prompt_plans(self, user_prompt):
        """
        Get detailed prompt plans for a list of txt files from Azure OpenAI based on the user prompt.

        Args:
            files (list): List of file paths.
            user_prompt (str): The user's prompt.

        Returns:
            str: Detailed prompt or error reason.
        """

        async with aiohttp.ClientSession() as session:
            plan = await self.get_prompt_plan(session, user_prompt)
            print(f"Completed preparing for: {user_prompt}")
            return plan
