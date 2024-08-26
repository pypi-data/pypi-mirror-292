import os
import sys
import json
import subprocess
import asyncio
import re

from .CodingAgent import CodingAgent
from .FormattingAgent import FormattingAgent
from .FileManagerAgent import FileManagerAgent
from .FileFinderAgent import FileFinderAgent
from .IdeaDevelopment import IdeaDevelopment
from .BugScannerAgent import BugScannerAgent
from .LongIdeaDevelopment import LongIdeaDevelopment
from .PromptAgent import PromptAgent
from .PrePromptAgent import PrePromptAgent
from .ReplacingAgent import ReplacingAgent
from .FileReplacingAgent import FileReplacingAgent
from .FileLightWorkingAgent import FileLightWorkingAgent
from .LanguageAgent import LanguageAgent
from .TechnicalExplainerAgent import TechnicalExplainerAgent
from .LightCodeAgent import LightCodeAgent


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from xcodeOperation.XcodeProjectManager import XcodeProjectManager
from xcodeOperation.XcodeRunner import XcodeRunner
from Scanner1.ProjectScanner1 import ProjectScanner1

class ControllerAgent:
    def __init__(self, role, directory_path, api_key, endpoint, deployment_id, max_tokens, schema):
        self.directory_path = directory_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.schema = schema
        self.role = role
        self.idea = IdeaDevelopment(role, os.path.join(directory_path, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.bug_scanner = BugScannerAgent(role, os.path.join(directory_path, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.long = LongIdeaDevelopment(role, os.path.join(directory_path, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.prompt = PromptAgent(role, os.path.join(directory_path, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.preprompt = PrePromptAgent(role, os.path.join(directory_path, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.coder = CodingAgent(role, os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.xcode_operations = XcodeProjectManager(os.path.join(directory_path))
        self.xcode_runner = XcodeRunner(role, os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.format = FormattingAgent(role, os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.lightCode = LightCodeAgent(role, os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.replace = ReplacingAgent(role, os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.fileManager = FileManagerAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.fileFinder = FileFinderAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.replaceFinder = FileReplacingAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.lightWorkFinder = FileLightWorkingAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.lang = LanguageAgent(role, os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.techExplainer = TechnicalExplainerAgent(role, os.path.join(directory_path, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.scanner = ProjectScanner1(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)

    def get_tree_txt_files(self):
        """Scan for tree.txt files in the specified directory."""
        tree_txt_files = []
        tree_path = os.path.join(self.directory_path, "Zinley/Project_analysis")

        if not os.path.exists(tree_path):
            print(f"Directory does not exist: {tree_path}")
            return tree_txt_files

        for root, _, files in os.walk(tree_path):
            for file in files:
                if file == 'tree.txt':
                    file_path = os.path.join(root, file)
                    tree_txt_files.append(file_path)

        return tree_txt_files

    def get_txt_files(self):
        """Scan for all txt files in the specified directory."""
        txt_files = []
        txt_path = os.path.join(self.directory_path, "Zinley/Project_analysis")

        if not os.path.exists(txt_path):
            print(f"Directory does not exist: {txt_path}")
            return txt_files

        for root, _, files in os.walk(txt_path):
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
            print(f"Failed to read file {file_path}: {e}")
            return None

    async def get_explainer(self, files, user_prompt, language):
        """Generate idea plans based on user prompt and available files."""
        return await self.techExplainer.get_technical_plans(files, user_prompt, language)

    async def get_prompt(self, user_prompt):
        """Generate idea plans based on user prompt and available files."""
        return await self.prompt.get_prompt_plans(user_prompt)

    async def get_prePrompt(self, files, user_prompt):
        """Generate idea plans based on user prompt and available files."""
        return await self.preprompt.get_prePrompt_plans(files, user_prompt)

    async def get_idea_plans(self, user_prompt):
        """Generate idea plans based on user prompt and available files."""
        return await self.idea.get_idea_plans(user_prompt)

    async def get_bugs_plans(self, files, user_prompt):
        """Generate idea plans based on user prompt and available files."""
        return await self.bug_scanner.get_idea_plans(files, user_prompt)

    async def get_long_idea_plans(self, files, user_prompt, is_first):
        """Generate idea plans based on user prompt and available files."""
        return await self.long.get_idea_plans(files, user_prompt, is_first)

    async def get_file_planning(self, idea_plan, tree):
        """Generate file planning based on idea plan and directory tree."""
        return await self.fileManager.get_file_plannings(idea_plan, tree)

    async def get_adding_file_planning(self, idea_plan, tree):
        """Generate file planning for adding new files based on idea plan and directory tree."""
        return await self.fileManager.get_adding_file_plannings(idea_plan, tree)

    async def get_moving_file_planning(self, idea_plan, tree):
        """Generate file planning for adding new files based on idea plan and directory tree."""
        return await self.fileManager.get_moving_file_plannings(idea_plan, tree)

    async def get_formatting_files(self, prompt, tree):
        """Generate formatting plans based on user prompt and directory tree."""
        return await self.fileFinder.get_file_plannings(prompt, tree)

    async def get_replacing_files(self, prompt, files):
        """Generate replacing plans based on user prompt and available files."""
        return await self.replaceFinder.get_file_plannings(prompt, files)

    async def get_working_files(self, prompt, files):
        """Generate replacing plans based on user prompt and available files."""
        return await self.lightWorkFinder.get_file_plannings(prompt, files)

    async def scan_and_update(self, files):
        """Scan updated files and log the updates."""
        print(f"Final step: {list(files)}")
        await self.scanner.scanning_files(list(files))
        return 'Done!'

    async def run_requests(self, request_list):
        """Run Xcode project requests."""
        return await self.xcode_runner.run_xcode_project(request_list, self.schema)

    async def process_creation(self, data):
        """Process the creation of new files based on provided data."""
        if data.get('Is_creating'):
            processes = data.get('Adding_new_files', [])
            await self.xcode_operations.execute_files_creation(processes)
            await self.update_tree()

    async def process_moving(self, data):
        """Process the creation of new files based on provided data."""
        if data.get('Is_moving'):
            processes = data.get('Moving_new_files', [])
            await self.xcode_operations.execute_files_creation(processes)
            await self.update_tree()

    async def build_existing_context(self, existing_files):
        """Build and return the context of existing files."""
        all_path = self.scan_needed_files(existing_files)
        all_context = ""

        for path in all_path:
            file_context = self.read_file_content(path)
            all_context += f"\n\nFile: {path}:\n{file_context}"

        return all_context

    async def get_coding_requests(self, instructions, context):
        """Generate coding requests based on instructions and context."""
        self.coder.initial_setup(instructions, context)
        is_first = True
        title = ""
        totalfile = set()
        while True:
            result = await self.coder.get_coding_requests(is_first, title)

            Is_Completed = result['Is_Completed']
            is_first = False
            title = result['Title']
            Purpose_detail = result['Title']
            file_name = result['file_name']
            totalfile.update([file_name])
            code = result['code']
            if code == "":
                print(f"Break Code within get_coding_requests func")
                break
            print(f"Working on: {Purpose_detail}")
            main_path = self.coder.scan_for_single_file(file_name)
            await self.replace_all_code_in_file(main_path, code)
            if Is_Completed == "True" or Purpose_detail == "All tasks completed":
                break

        self.coder.clear_conversation_history()
        return totalfile

    async def replace_all_code_in_file(self, file_path, new_code_snippet):
        """Replace the entire content of a file with the new code snippet."""
        try:
            with open(file_path, 'w') as file:
                if self.contains_markdown_code(new_code_snippet):
                    cleaned_code = self.remove_markdown_code(new_code_snippet)
                    file.write(cleaned_code)
                else:
                    file.write(new_code_snippet)
            print(f"The codes have been successfully written in... {file_path}.")
        except Exception as e:
            print(f"Error writing code. Error: {e}")

    def contains_markdown_code(self, content):
        """Check if the content contains markdown code blocks."""
        markdown_code_pattern = r'```[\w]*[\s\S]*?```'  # code blocks with language specification
        return bool(re.search(markdown_code_pattern, content, re.MULTILINE))

    def remove_markdown_code(self, content):
        """This function removes the first and last lines if they are markdown code block delimiters."""
        lines = content.splitlines()

        if lines and lines[0].startswith('```') and lines[-1].startswith('```'):
            lines = lines[1:-1]

        return '\n'.join(lines).strip()

    async def code_format_pipeline(self, finalPrompt):
        """Pipeline for code formatting."""
        print("code_format_pipeline")
        await self.update_tree()
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()
        print("Now, I am working on file processing")
        file_result = await self.get_formatting_files(finalPrompt, tree)
        print(file_result)
        await self.process_creation(file_result)
        print("Completed processing files")
        print(f"Next, I will start the formatting/refactoring phase")
        working_files = file_result.get('working_files', [])
        print(f"Formatting: {working_files}")
        if working_files:
            await self.format.get_formats(working_files, finalPrompt)
            self.format.clear_conversation_history()
            print(f"Next, I will build to check if any compile error was made")
            all_fixing_files = await self.build_and_fix_compile_error(working_files)
            print(f"all_fixing_files: {all_fixing_files}")
            all_final_files = set()
            all_final_files.update(working_files)
            all_final_files.update(all_fixing_files)
            print(f"Formatting/refactoring phase done")
            if all_final_files:
                await self.scan_and_update(all_final_files)

    async def build_and_fix_compile_error(self, file_list):
        """Build project and fix compile errors."""
        await self.update_tree()
        final_files = await self.run_requests(file_list)
        return final_files

    async def fix_compile_error_pipeline(self, file_list):
        """Pipeline for fixing compile errors."""
        print("fix_compile_error_pipeline")
        final_files = await self.build_and_fix_compile_error(file_list)
        if len(final_files) > 0:
            await self.scan_and_update(final_files)

    async def add_files_folders_pipeline(self, finalPrompt):
        """Pipeline for adding files and folders."""
        tree = self.get_tree_txt_files()
        print("add_files_folders_pipeline")
        await self.update_tree()
        print("Now, I am working on file processing")
        file_result = await self.get_adding_file_planning(finalPrompt, tree)
        await self.process_creation(file_result)
        files = []
        if file_result.get('Is_creating'):
            processes = file_result.get('Adding_new_files', [])
            for process in processes:
                file_name = process['Parameters']['file_name']
                files.append(file_name)
        files = [file for file in files if file]
        if files:
            await self.scan_and_update(files)


    async def move_files_folders_pipeline(self, finalPrompt):
        """Pipeline for adding files and folders."""
        tree = self.get_tree_txt_files()
        print("move_files_folders_pipeline")
        await self.update_tree()
        print("Now, I am working on file processing")
        file_result = await self.get_moving_file_planning(finalPrompt, tree)
        print(file_result)
        await self.process_moving(file_result)

    async def replace_code_pipeline(self, finalPrompt):
        """Pipeline for replacing code."""
        print("replace_code_pipeline")
        await self.update_tree()
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()
        print("Now, I am working on file processing")
        file_result = await self.get_replacing_files(finalPrompt, files)
        print(file_result)
        await self.process_creation(file_result)
        print("Completed processing files")
        print(f"Next, I will start the replacing phase")
        working_files = file_result.get('working_files', [])
        print(f"Replacing: {working_files}")
        if working_files:
            await self.format.get_formats(working_files, finalPrompt)
            self.format.clear_conversation_history()
            print(f"Next, I will build to check if any compile error was made")
            all_fixing_files = await self.build_and_fix_compile_error(working_files)
            print(f"all_fixing_files: {all_fixing_files}")
            all_final_files = set()
            all_final_files.update(working_files)
            all_final_files.update(all_fixing_files)
            print(f"Replacing phase done")
            if all_final_files:
                await self.scan_and_update(all_final_files)

    async def regular_code_task_pipeline(self, finalPrompt):
        """Pipeline for regular coding tasks."""
        print("regular_code_task_pipeline")
        await self.update_tree()
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()
        self.idea.initial_setup(files)
        print("Now I will create an initial development plan for clarification.")

        idea_plan = await self.get_idea_plans(finalPrompt)

        print(f"This is my initial development plan: {idea_plan}")

        
        while True:
            print("Are you satisfied with this development plan? Enter \"yes\" if satisfied, or provide feedback for modifications: ")
            user_prompt = input("").lower()
            if user_prompt == "" or user_prompt == "yes" or user_prompt == "y":
                break
            else:
                print(f"Let's me update my development plan!")
                eng_prompt = await self.lang.get_language_plans(user_prompt)
                idea_plan = await self.idea.get_idea_plans(eng_prompt)
                print(f"This is my updated development plan: {idea_plan}")

        print("Now, I am working on file processing")
        file_result = await self.get_file_planning(idea_plan, tree)
        await self.process_creation(file_result)
        print("Completed processing files")
        print(f"Next, I will start the coding phase")
        existing_files = file_result.get('Existing_files', [])
        final_existing_files = set()
        final_existing_files.update(os.path.basename(file) for file in existing_files)
        all_context = await self.build_existing_context(list(final_existing_files))
        totalfile = await self.get_coding_requests(idea_plan, all_context)

        print(f"Next, I will build to check if any compile error was made")
        all_fixing_files = await self.build_and_fix_compile_error(totalfile)
        print(f"all_fixing_files: {all_fixing_files}")
        all_final_files = set()
        all_final_files.update(totalfile)
        all_final_files.update(all_fixing_files)
        print(f"Coding phase done")
        if all_final_files:
            await self.scan_and_update(all_final_files)

    async def light_code_task_pipeline(self, finalPrompt):
        """Pipeline for light code."""
        print("light_code_task_pipeline")
        await self.update_tree()
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()
        print("Now, I am working on file processing")
        file_result = await self.get_working_files(finalPrompt, files)
        print(file_result)
        await self.process_creation(file_result)
        print("Completed processing files")
        print(f"Next, I will start the coding phase")
        working_files = file_result.get('working_files', [])
        print(f"working on: {finalPrompt}")
        if working_files:
            processed_files = await self.lightCode.get_workings(working_files)
            self.lightCode.clear_conversation_history()
            print(f"Next, I will build to check if any compile error was made")
            all_fixing_files = await self.build_and_fix_compile_error(processed_files)
            print(f"all_fixing_files: {all_fixing_files}")
            all_final_files = set()
            all_final_files.update(processed_files)
            all_final_files.update(all_fixing_files)
            print(f"Writting phase done")
            if all_final_files:
                print(all_final_files)
                await self.scan_and_update(all_final_files)


    async def major_code_task_pipeline(self, finalPrompt):
        """Pipeline for major coding tasks."""
        print("major_code_task_pipeline")

        # Get the list of text files and the directory tree
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()

        # Initial setup with the provided final prompt
        self.prompt.initial_setup(files, finalPrompt)
        prompt = await self.get_prompt(finalPrompt)

        # Process each milestone
        while True:
            milestones = prompt.get('milestones', [])
            print("This may be a long run, I will split this into some big processes:")
            for milestone in milestones:
                goal = milestone['Goal']
                print(goal)

            # feedback_prompt = input("Press enter to go next, or provide feedback for modifications: ")
            # print("Are you satisfied with this development plan? Enter \"yes\" if satisfied, or provide feedback for modifications: ")
            # if feedback_prompt == "":
            print("Enter \"yes\" to proceed, or provide feedback for modifications: ")
            feedback_prompt = input("").lower()
            if feedback_prompt == "" or feedback_prompt == "yes" or feedback_prompt == "y":
                break
            else:
                print(f"Let's me update your request!")
                eng_prompt = await self.lang.get_language_plans(feedback_prompt)
                prompt = await self.get_prompt(eng_prompt)

        # Long-term setup
        self.long.initial_setup(finalPrompt)
        is_first = True
        self.prompt.clear_conversation_history()
        milestones = prompt.get('milestones', [])

        # Iterate through each milestone to process
        for milestone in milestones:
            await self.update_tree()
            goal = milestone['Goal']
            implementation_prompt = milestone['implementation_prompt']
            print(f"Working on: {goal}")

            print(f"Now I will create an initial development plan for clarification.")

            idea_plan = await self.get_long_idea_plans(files, implementation_prompt, is_first)
            is_first = False

            print(f"This is my initial development plan: {idea_plan} for {goal}")

            isModified = False
            while True:
                print("Are you satisfied with this development plan? Enter \"yes\" if satisfied, or provide feedback for modifications: ")
                user_prompt = input().lower()
                if user_prompt == "" or user_prompt == "yes" or user_prompt == "y":
                    if isModified:
                        self.long.feedback_history = []
                        self.long.feedback_history = self.long.conversation_history
                        self.long.conversation_history[-1] = {"role": "assistant", "content": idea_plan}
                    break
                else:
                    print(f"Let's me update my development plan!")
                    eng_prompt = await self.lang.get_language_plans(user_prompt)
                    idea_plan = await self.long.get_feedback_plans(eng_prompt)
                    print(f"This is my updated development plan: {idea_plan}")
                    isModified = True

            print("Now, I am working on file processing")
            file_result = await self.get_file_planning(idea_plan, tree)
            await self.process_creation(file_result)
            print("Completed processing files")

            print(f"Next, I will start the coding phase")
            existing_files = file_result.get('Existing_files', [])
            final_existing_files = set()
            final_existing_files.update(os.path.basename(file) for file in existing_files)
            all_context = await self.build_existing_context(list(final_existing_files))
            totalfile = await self.get_coding_requests(idea_plan, all_context)

            print(f"Next, I will build to check if any compile error was made")
            all_fixing_files = await self.build_and_fix_compile_error(totalfile)
            all_final_files = set()
            all_final_files.update(totalfile)
            all_final_files.update(all_fixing_files)
            print(f"Coding phase done")

            if all_final_files:
                await self.scan_and_update(all_final_files)

        self.long.clear_conversation_history()


    async def explainer_task_pipeline(self, files, finalPrompt, language):
        print("explainer_task_pipeline")
        print(await self.get_explainer(files, finalPrompt, language))

    async def get_started(self, user_prompt):
        """Start the processing of the user prompt."""
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()

        print("Hi I am Zinley, I will process your prompt now")

        prePrompt = await self.get_prePrompt(files, user_prompt)
        finalPrompt = prePrompt['processed_prompt']
        pipeline = prePrompt['pipeline']
        language = prePrompt['original_prompt_language']
        await self.update_tree()
        if pipeline == "0":
            await controller.explainer_task_pipeline(files, finalPrompt, language)
        elif pipeline == "1":
            await self.code_format_pipeline(finalPrompt)
        elif pipeline == "2":
            await self.fix_compile_error_pipeline(list())  # add a missing parameter
        elif pipeline == "3":
            await self.replace_code_pipeline(finalPrompt)
        elif pipeline == "4":
            await self.add_files_folders_pipeline(finalPrompt)
        elif pipeline == "5":
            await self.move_files_folders_pipeline(finalPrompt)
        elif pipeline == "6":
            await self.light_code_task_pipeline(finalPrompt)
        elif pipeline == "7":
            await self.regular_code_task_pipeline(finalPrompt)
        elif pipeline == "8":
            await self.major_code_task_pipeline(finalPrompt)

        print(f"Done work for: {user_prompt}")

async def main():
    """Main execution entry point."""
    project_path = "/Users/hoangnm/Documents/workspace/projects/zinley/fsd_v2_universal/v2/projects/DemoApp"
    api_key = os.getenv("OPENAI_API_KEY", "96ae909e40534d49a70c5e4bdfe54f62")
    endpoint = "https://zinley.openai.azure.com"
    deployment_id = "hi"
    role = "iOS developer"
    max_tokens = 4096
    user_prompt = input("What do you want to build? ")
    controller = ControllerAgent(role, project_path, api_key, endpoint, deployment_id, max_tokens)
    files = controller.get_txt_files()
    tree = controller.get_tree_txt_files()

    print("Hi I am Zinley, I will process your prompt now")

    prePrompt = await controller.get_prePrompt(files, user_prompt)
    print(prePrompt)
    finalPrompt = prePrompt['processed_prompt']
    pipeline = prePrompt['pipeline']
    language = prePrompt['original_prompt_language']
    await controller.update_tree()
    if pipeline == "0":
        await controller.explainer_task_pipeline(files, finalPrompt, language)
    elif pipeline == "1":
        await controller.code_format_pipeline(finalPrompt)
    elif pipeline == "2":
        await controller.fix_compile_error_pipeline(list())  # add a missing parameter
    elif pipeline == "3":
        await controller.replace_code_pipeline(finalPrompt)
    elif pipeline == "4":
        await controller.add_files_folders_pipeline(finalPrompt)
    elif pipeline == "5":
        await controller.move_files_folders_pipeline(finalPrompt)
    elif pipeline == "6":
        await controller.light_code_task_pipeline(finalPrompt)
    elif pipeline == "7":
        await controller.regular_code_task_pipeline(finalPrompt)
    # elif pipeline == "8":
    #     await controller.major_code_task_pipeline(finalPrompt)

    print(f"Done work for: {user_prompt}")

if __name__ == "__main__":
    asyncio.run(main())
