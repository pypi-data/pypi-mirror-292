import os
import json
import asyncio
from .ExplainablePrePromptAgent import ExplainablePrePromptAgent
from .GeneralExplainerAgent import GeneralExplainerAgent
from .ExplainableFileFinderAgent import ExplainableFileFinderAgent
from .MainExplainerAgent import MainExplainerAgent

import sys
import subprocess
import re

class ExplainerController:

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

        self.preprompt = ExplainablePrePromptAgent(os.path.join(directory_path, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.normalExplainer = GeneralExplainerAgent(os.path.join(directory_path, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.mainExplainer = MainExplainerAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.fileFinder = ExplainableFileFinderAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)

    async def get_prePrompt(self, user_prompt):
        """Generate idea plans based on user prompt and available files."""
        return await self.preprompt.get_prePrompt_plans(user_prompt)

    async def get_normal_answer(self, user_prompt, language):
        """Generate idea plans based on user prompt and available files."""
        return await self.normalExplainer.get_normal_answer_plans(user_prompt, language)

    async def get_file_answer(self, user_prompt, language, files):
        """Generate idea plans based on user prompt and available files."""
        return await self.mainExplainer.get_answer_plans(user_prompt, language, files)

    async def get_explaining_files(self, prompt, files):
        """Generate idea plans based on user prompt and available files."""
        await self.update_tree()
        return await self.fileFinder.get_file_plannings(prompt, files)

    def get_txt_files(self):
        """Scan for all txt files in the specified directory."""
        txt_files = []
        txt_path = self.directory_path + "/Zinley/Project_analysis"

        if not os.path.exists(txt_path):
            print(f"Directory does not exist: {txt_path}")
            return txt_files

        for root, dirs, files in os.walk(txt_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    txt_files.append(file_path)

        return txt_files

    async def update_tree(self):
        """Update the project directory tree and save to tree.txt."""
        tree_path = self.directory_path
        output_dir = os.path.join(tree_path, "Zinley", "Project_analysis")
        os.makedirs(output_dir, exist_ok=True)
        tree_file_path = os.path.join(output_dir, "tree.txt")
        # Open the file to write the tree output
        with open(tree_file_path, 'w') as f:
            # Run the tree command and capture the output
            result = subprocess.run(['tree', self.directory_path, '-I', 'Zinley'], stdout=subprocess.PIPE, text=True)
            # Write the output to the file
            f.write(result.stdout)

    def scan_needed_files(self, filenames):
        """Scan for specified files in the specified directory."""
        found_files = []

        if not os.path.exists(self.directory_path):
            print(f"Directory does not exist: {self.directory_path}")
            return found_files

        for root, dirs, files in os.walk(self.directory_path):
            for filename in filenames:
                if filename in files:
                    file_path = os.path.join(root, filename)
                    found_files.append(file_path)

        return found_files

    def read_file_content(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return None

    async def get_started(self, user_prompt):
        files = self.get_txt_files()

        print("Hi I am Zinley, I will process your prompt now")

        prePrompt = await self.get_prePrompt(user_prompt)
        finalPrompt = prePrompt['processed_prompt']
        pipeline = prePrompt['pipeline']
        language = prePrompt['original_prompt_language']

        if pipeline == "1":
            file_result = await self.get_explaining_files(finalPrompt, files)
            working_files = file_result.get('working_files', [])
            if working_files:
                print(await self.get_file_answer(finalPrompt, language, working_files))
            else:
                print("Hi, I am Zinley. I can't support this right now because I am having trouble accessing the file context to answer your question. Please try again! I am sorry for any inconvenience this may cause.")
        elif pipeline == "2":
            print(await self.get_normal_answer(finalPrompt, language))
