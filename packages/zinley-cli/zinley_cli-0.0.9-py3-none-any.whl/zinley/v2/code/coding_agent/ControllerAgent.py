import os
import shutil
import sys
import json
import subprocess
import asyncio
import re

from zinley.v2.code.util import utils

from .CodingAgent import CodingAgent
from .FormattingAgent import FormattingAgent
from .FileManagerAgent import FileManagerAgent
from .FileFinderAgent import FileFinderAgent
from .IdeaDevelopment import IdeaDevelopment
from .BugScannerAgent import BugScannerAgent
from .LongIdeaDevelopment import LongIdeaDevelopment
from .PromptAgent import PromptAgent
from .PrePromptAgent import PrePromptAgent
from .FileReplacingAgent import FileReplacingAgent
from .FileLightWorkingAgent import FileLightWorkingAgent
from .LanguageAgent import LanguageAgent
from .TechnicalExplainerAgent import TechnicalExplainerAgent
from .LightCodeAgent import LightCodeAgent
from .TechStackAgent import TechStackAgent


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MainOperation.ProjectManager import ProjectManager
from MainOperation.ProjectsRunner import ProjectsRunner
from Scanner1.ProjectScanner1 import ProjectScanner1
from zinley.v2.code.log.logger_config import get_logger
logger = get_logger(__name__)

HOME_DIRECTORY = os.path.expanduser('~')
HIDDEN_ZINLEY_FOLDER = '.zinley'
class ControllerAgent:
    def __init__(self, directory_path, api_key, endpoint, deployment_id, max_tokens, scheme):
        part = directory_path.split('/')
        project_name = part[-1]
        self.directory_path = directory_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.scheme = scheme
        self.idea = IdeaDevelopment(os.path.join(directory_path), os.path.join(HOME_DIRECTORY, HIDDEN_ZINLEY_FOLDER, project_name, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.bug_scanner = BugScannerAgent(os.path.join(HOME_DIRECTORY, HIDDEN_ZINLEY_FOLDER, project_name, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.long = LongIdeaDevelopment(os.path.join(HOME_DIRECTORY, HIDDEN_ZINLEY_FOLDER, project_name, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.prompt = PromptAgent(os.path.join(HOME_DIRECTORY, HIDDEN_ZINLEY_FOLDER, project_name, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.preprompt = PrePromptAgent(os.path.join(HOME_DIRECTORY, HIDDEN_ZINLEY_FOLDER, project_name, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.coder = CodingAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.project = ProjectManager(os.path.join(directory_path))
        self.runner = ProjectsRunner(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens, scheme)
        self.format = FormattingAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.lightCode = LightCodeAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.fileManager = FileManagerAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.fileFinder = FileFinderAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.replaceFinder = FileReplacingAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.lightWorkFinder = FileLightWorkingAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.lang = LanguageAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.techExplainer = TechnicalExplainerAgent(os.path.join(HOME_DIRECTORY, HIDDEN_ZINLEY_FOLDER, project_name, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.scanner = ProjectScanner1(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.techStackAgent = TechStackAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)

    def get_tree_txt_files(self):
        """Scan for tree.txt files in the specified directory."""
        tree_txt_files = []
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = self.directory_path.split('/')
        project_name = parts[-1]
        tree_path = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")

        if not os.path.exists(tree_path):
            logger.debug(f"Directory does not exist: {tree_path}")
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
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = self.directory_path.split('/')
        project_name = parts[-1]
        txt_path = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
        # txt_path = os.path.join(self.directory_path, "Zinley/Project_analysis")

        if not os.path.exists(txt_path):
            logger.debug(f"Directory does not exist: {txt_path}")
            return txt_files

        for root, _, files in os.walk(txt_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    txt_files.append(file_path)

        return txt_files

    def scan_for_single_file(self, filename):
        """
        Scan for a single specified file in the specified directory.
        Args:
            filename (str): The name of the file to look for.
        Returns:
            str: Path to the specified file if found, else None.
        """
        # Check if the specified directory exists
        if not os.path.exists(self.directory_path):
            print(f"Directory does not exist: {self.directory_path}")
            return None

        # Walk through the directory and look for the specified file
        for root, _, files in os.walk(self.directory_path):
            if filename in files:
                # Return the full path to the file if found
                return os.path.join(root, filename)

        # If the file wasn't found, print an error message and return None
        print(f"Couldn't find {filename} in: {self.directory_path}")
        return None

    async def update_tree(self):
        """Update the project directory tree and save to tree.txt."""
        tree_path = self.directory_path
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = tree_path.split('/')
        project_name = parts[-1]
        output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
        os.makedirs(output_dir, exist_ok=True)
        tree_file_path = os.path.join(output_dir, "tree.txt")
        # Open the file to write the tree output
        with open(tree_file_path, 'w') as f:
            utils.tree(self.directory_path, exclude="Zinley", stdout=f)

    def scan_needed_files(self, filenames):
        """Scan for specified files in the specified directory."""
        found_files = []

        if not os.path.exists(self.directory_path):
            logger.debug(f"Directory does not exist: {self.directory_path}")
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
            logger.error(f"Failed to read file {file_path}: {e}")
            return None

    async def get_explainer(self, files, user_prompt, language, role):
        """Generate idea plans based on user prompt and available files."""
        return await self.techExplainer.get_technical_plans(files, user_prompt, language, role)

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

    async def get_working_files(self, prompt, files, role):
        """Generate replacing plans based on user prompt and available files."""
        return await self.lightWorkFinder.get_file_plannings(prompt, files, role)

    async def scan_and_update(self, files):
        """Scan updated files and log the updates."""
        logger.debug(f"Final step: {list(files)}")
        await self.scanner.scanning_files(list(files))
        return 'Done!'


    async def totalScan(self):
        """Scan updated files and log the updates."""
        logger.info(f"Re-scanning in progress....")
        await self.scanner.get_started()
        return 'Done!'

    async def run_requests(self, request_list, role):
        """Run project requests."""
        return await self.runner.run_project(request_list, role, self.scheme)

    async def process_creation(self, data):
        """Process the creation of new files based on provided data."""
        if data.get('Is_creating'):
            processes = data.get('Adding_new_files', [])
            await self.project.execute_files_creation(processes)
            await self.update_tree()

    async def process_moving(self, data):
        """Process the creation of new files based on provided data."""
        if data.get('Is_moving'):
            processes = data.get('Moving_new_files', [])
            await self.project.execute_files_creation(processes)
            await self.update_tree()

    async def build_existing_context(self, existing_files):
        """Build and return the context of existing files."""
        all_path = self.scan_needed_files(existing_files)
        all_context = ""

        for path in all_path:
            file_context = self.read_file_content(path)
            all_context += f"\n\nFile: {path}:\n{file_context}"

        return all_context

    async def get_coding_requests(self, instructions, final_working_files, context, context_files, role):
        """Generate coding requests based on instructions and context."""
        self.coder.initial_setup(context_files, instructions, context, role)
        is_first = True
        title = ""
        final_working_files = [file for file in final_working_files if file]

        lists = await self.techStackAgent.get_file_plannings(final_working_files)
        working_files = lists.get('working_files', [])

        # Looping through the dictionary
        for filename, techStack in working_files.items():
            result = await self.coder.get_coding_requests(is_first, title, filename, techStack)
            is_first = False
            title = result['Title']
            code = result['code']
            print(f"Working on {filename}: {title}")
            main_path = self.scan_for_single_file(filename)
            await self.replace_all_code_in_file(main_path, code)

        return final_working_files

    async def replace_all_code_in_file(self, file_path, new_code_snippet):
        """Replace the entire content of a file with the new code snippet."""
        try:
            with open(file_path, 'w') as file:
                file.write(new_code_snippet)
            logger.debug(f"The codes have been successfully written in... {file_path}.")
        except Exception as e:
            logger.error(f"Error writing code. Error: {e}")

    async def code_format_pipeline(self, finalPrompt, role):
        """Pipeline for code formatting."""
        logger.debug("code_format_pipeline")
        await self.update_tree()
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()
        logger.info("Now, I am working on file processing")
        file_result = await self.get_formatting_files(finalPrompt, tree)
        logger.info(file_result)
        await self.process_creation(file_result)
        logger.info("Completed processing files")
        logger.info(f"Next, I will start the formatting/refactoring phase")
        working_files = file_result.get('working_files', [])
        logger.info(f"Formatting: {working_files}")
        if working_files:
            await self.format.get_formats(working_files, finalPrompt, role)
            self.format.clear_conversation_history()
            logger.info(f"Next, I will build to check if any compile error was made")
            all_fixing_files = await self.build_and_fix_compile_error(working_files, role)
            logger.debug(f"all_fixing_files: {all_fixing_files}")
            all_final_files = set()
            all_final_files.update(working_files)
            all_final_files.update(all_fixing_files)
            logger.info(f"Formatting/refactoring phase done")
            if all_final_files:
                await self.scan_and_update(all_final_files)

    async def build_and_fix_compile_error(self, file_list, role):
        """Build project and fix compile errors."""
        await self.update_tree()
        final_files = await self.run_requests(file_list, role)
        return final_files

    async def fix_compile_error_pipeline(self, file_list, role):
        """Pipeline for fixing compile errors."""
        logger.info("fix_compile_error_pipeline")
        final_files = await self.build_and_fix_compile_error(file_list, role)
        if len(final_files) > 0:
            await self.scan_and_update(final_files)

    async def add_files_folders_pipeline(self, finalPrompt, role):
        """Pipeline for adding files and folders."""
        tree = self.get_tree_txt_files()
        logger.debug("add_files_folders_pipeline")
        await self.update_tree()
        logger.info("Now, I am working on file processing")
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

    async def move_files_folders_pipeline(self, finalPrompt, role):
        """Pipeline for adding files and folders."""
        tree = self.get_tree_txt_files()
        logger.debug("move_files_folders_pipeline")
        await self.update_tree()
        logger.info("Now, I am working on file processing")
        file_result = await self.get_moving_file_planning(finalPrompt, tree)
        logger.info(file_result)
        await self.process_moving(file_result)

    async def replace_code_pipeline(self, finalPrompt, role):
        """Pipeline for replacing code."""
        logger.debug("replace_code_pipeline")
        await self.update_tree()
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()
        logger.info("Now, I am working on file processing")
        file_result = await self.get_replacing_files(finalPrompt, files)
        logger.info(file_result)
        await self.process_creation(file_result)
        logger.info("Completed processing files")
        logger.info(f"Next, I will start the replacing phase")
        working_files = file_result.get('working_files', [])
        logger.debug(f"Replacing: {working_files}")
        if working_files:
            await self.format.get_formats(working_files, finalPrompt, role)
            self.format.clear_conversation_history()
            logger.info(f"Next, I will build to check if any compile error was made")
            all_fixing_files = await self.build_and_fix_compile_error(working_files, role)
            logger.debug(f"all_fixing_files: {all_fixing_files}")
            all_final_files = set()
            all_final_files.update(working_files)
            all_final_files.update(all_fixing_files)
            logger.info(f"Replacing phase done")
            if all_final_files:
                await self.scan_and_update(all_final_files)

    async def regular_code_task_pipeline(self, finalPrompt, role):
        """Pipeline for regular coding tasks."""
        logger.debug("regular_code_task_pipeline")
        await self.update_tree()
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()
        self.idea.initial_setup(files, role)
        logger.info("Now I will create an initial development plan for clarification.")

        idea_plan = await self.get_idea_plans(finalPrompt)

        logger.info(f"This is my initial development plan: {idea_plan}")

        while True:
            logger.info(
                "Are you satisfied with this development plan? Enter \"yes\" if satisfied, or provide feedback for modifications: ")

            user_prompt_json = input()
            user_prompt, file_attachment = parse_payload(user_prompt_json, self.directory_path)
            user_prompt = user_prompt.lower()

            if user_prompt == "" or user_prompt == "yes" or user_prompt == "y":
                break
            else:
                logger.info(f"Let's me update my development plan!")
                eng_prompt = await self.lang.get_language_plans(user_prompt, role)
                idea_plan = await self.idea.get_idea_plans(eng_prompt)
                logger.info(f"This is my updated development plan: {idea_plan}")

        logger.info("Now, I am working on file processing")
        file_result = await self.get_file_planning(idea_plan, tree)
        await self.process_creation(file_result)
        logger.info("Completed processing files")
        logger.info(f"Next, I will start the coding phase")
        existing_files = file_result.get('Existing_files', [])
        new_adding_files = []
        context_files = file_result.get('Context_files', [])
        adding_new_files = file_result.get('Adding_new_files', [])
        if adding_new_files:
            for item in adding_new_files:
                new_adding_files.append(item['Parameters']['file_name'])

        final_working_files = set()
        final_working_files.update(existing_files)
        final_working_files.update(new_adding_files)
        final_existing_files = set()
        final_existing_files.update(os.path.basename(file) for file in existing_files)
        all_context = await self.build_existing_context(list(final_existing_files))
        totalfile = await self.get_coding_requests(idea_plan, list(final_working_files), all_context, context_files, role)
        logger.info(f"Next, I will build to check if any compile error was made")
        all_fixing_files = await self.build_and_fix_compile_error(totalfile, role)
        logger.debug(f"all_fixing_files: {all_fixing_files}")
        all_final_files = set()
        all_final_files.update(totalfile)
        all_final_files.update(all_fixing_files)
        logger.info(f"Coding phase done")
        if all_final_files:
            await self.scan_and_update(all_final_files)

    async def light_code_task_pipeline(self, finalPrompt, role):
        """Pipeline for light code."""
        logger.debug("light_code_task_pipeline")
        await self.update_tree()
        files = self.get_txt_files()
        logger.info("Now, I am working on file processing")
        file_result = await self.get_working_files(finalPrompt, files, role)
        logger.info(file_result)
        await self.process_creation(file_result)
        logger.info("Completed processing files")
        logger.info(f"Next, I will start the coding phase")
        working_files = file_result.get('working_files', [])
        logger.info(f"working on: {finalPrompt}")
        if working_files:
            processed_files = await self.lightCode.get_workings(working_files, role)
            self.lightCode.clear_conversation_history()
            logger.info(f"Next, I will build to check if any compile error was made")
            all_fixing_files = await self.build_and_fix_compile_error(processed_files, role)
            logger.debug(f"all_fixing_files: {all_fixing_files}")
            all_final_files = set()
            all_final_files.update(processed_files)
            all_final_files.update(all_fixing_files)
            logger.info(f"Writting phase done")
            if all_final_files:
                logger.info(all_final_files)
                await self.scan_and_update(all_final_files)


    async def major_code_task_pipeline(self, finalPrompt, role):
        """Pipeline for major coding tasks."""
        """
        logger.info("major_code_task_pipeline")

        # Get the list of text files and the directory tree
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()

        # Initial setup with the provided final prompt
        self.prompt.initial_setup(files, finalPrompt, role)
        prompt = await self.get_prompt(finalPrompt)

        # Process each milestone
        while True:
            milestones = prompt.get('milestones', [])
            logger.info("This may be a long run, I will split this into some big processes:")
            for milestone in milestones:
                goal = milestone['Goal']
                logger.info(goal)

            feedback_prompt = input("Press enter to go next, or provide feedback for modifications: ")
            if feedback_prompt == "":
                break
            else:
                logger.info(f"Let's me update your request!")
                eng_prompt = await self.lang.get_language_plans(feedback_prompt)
                prompt = await self.get_prompt(eng_prompt)

        # Long-term setup
        self.long.initial_setup(finalPrompt, role)
        is_first = True
        self.prompt.clear_conversation_history()
        milestones = prompt.get('milestones', [])

        # Iterate through each milestone to process
        for milestone in milestones:
            await self.update_tree()
            goal = milestone['Goal']
            implementation_prompt = milestone['implementation_prompt']
            logger.info(f"Working on: {goal}")

            logger.info(f"Now I will create an initial development plan for clarification.")

            idea_plan = await self.get_long_idea_plans(files, implementation_prompt, is_first)
            is_first = False

            logger.info(f"This is my initial development plan: {idea_plan} for {goal}")

            isModified = False
            while True:
                user_prompt = input("Are you satisfied with this development plan? Press enter if yes, or provide feedback for modifications: ")
                if user_prompt == "":
                    if isModified:
                        self.long.feedback_history = []
                        self.long.feedback_history = self.long.conversation_history
                        self.long.conversation_history[-1] = {"role": "assistant", "content": idea_plan}
                    break
                else:
                    logger.info(f"Let's me update my development plan!")
                    eng_prompt = await self.lang.get_language_plans(user_prompt)
                    idea_plan = await self.long.get_feedback_plans(eng_prompt)
                    logger.info(f"This is my updated development plan: {idea_plan}")
                    isModified = True

            logger.info("Now, I am working on file processing")
            file_result = await self.get_file_planning(idea_plan, tree)
            await self.process_creation(file_result)
            logger.info("Completed processing files")

            logger.info(f"Next, I will start the coding phase")
            existing_files = file_result.get('Existing_files', [])
            final_existing_files = set()
            final_existing_files.update(os.path.basename(file) for file in existing_files)
            all_context = await self.build_existing_context(list(final_existing_files))
            totalfile = await self.get_coding_requests(idea_plan, all_context, role)

            logger.info(f"Next, I will build to check if any compile error was made")
            all_fixing_files = await self.build_and_fix_compile_error(totalfile, role)
            all_final_files = set()
            all_final_files.update(totalfile)
            all_final_files.update(all_fixing_files)
            logger.info(f"Coding phase done")

            if all_final_files:
                await self.scan_and_update(all_final_files)
                """
        self.long.clear_conversation_history()


    async def explainer_task_pipeline(self, files, finalPrompt, language, role):
        logger.debug("explainer_task_pipeline")
        logger.info(await self.get_explainer(files, finalPrompt, language, role))

    async def get_started(self, user_prompt):
        """Start the processing of the user prompt."""
        files = self.get_txt_files()
        tree = self.get_tree_txt_files()

        logger.info("Hi I am Zinley, I will process your prompt now")

        prePrompt = await self.get_prePrompt(files, user_prompt)
        role = prePrompt['role']
        finalPrompt = prePrompt['processed_prompt']
        pipeline = prePrompt['pipeline']
        language = prePrompt['original_prompt_language']
        need_to_re_scan = prePrompt['need_to_re_scan']

        if need_to_re_scan == "True":
            await self.totalScan()

        await self.update_tree()
        if pipeline == "0":

            await self.explainer_task_pipeline(files, finalPrompt, language, role)
        elif pipeline == "1":
            await self.code_format_pipeline(finalPrompt, role)
        elif pipeline == "2":
            await self.fix_compile_error_pipeline(list(), role)  # add a missing parameter
        elif pipeline == "3":
            await self.replace_code_pipeline(finalPrompt, role)
        elif pipeline == "4":
            await self.add_files_folders_pipeline(finalPrompt, role)
        elif pipeline == "5":
            await self.move_files_folders_pipeline(finalPrompt, role)
        elif pipeline == "6":
            await self.light_code_task_pipeline(finalPrompt, role)
        elif pipeline == "7":
            await self.regular_code_task_pipeline(finalPrompt, role)
        elif pipeline == "8":
            await self.major_code_task_pipeline(finalPrompt, role)

        logger.info(f"Done work for: {user_prompt}")


def parse_payload(user_prompt_json, project_path):
    try:
        file_path = None
        data = json.loads(user_prompt_json)
        user_prompt = data.get("prompt", "")
        file_path = data.get("file_path", None)
        if file_path and os.path.exists(file_path):
            logger.info(f"{file_path} exists. Moving the file to {project_path}")
            shutil.move(file_path, project_path)
        else:
            file_path = None
    except json.JSONDecodeError:
        # If input is not valid JSON, treat it as plain text
        user_prompt = user_prompt_json
        logger.info(f"Received Plain Text Prompt: {user_prompt}")

    return user_prompt, file_path

async def main():
    """Main execution entry point."""
    project_path = "../../projects/abcd"
    api_key = os.getenv("OPENAI_API_KEY", "96ae909e40534d49a70c5e4bdfe54f62")
    endpoint = "https://zinley.openai.azure.com"
    deployment_id = "hi"
    max_tokens = 4096
    user_prompt, file_attachment = parse_payload(user_prompt_json, self.directory_path)
    controller = ControllerAgent(project_path, api_key, endpoint, deployment_id, max_tokens)
    files = controller.get_txt_files()
    tree = controller.get_tree_txt_files()

    logger.info("Hi I am Zinley, I will process your prompt now")

    prePrompt = await controller.get_prePrompt(files, user_prompt)
    logger.debug(prePrompt)
    role = prePrompt['role']
    finalPrompt = prePrompt['processed_prompt']
    pipeline = prePrompt['pipeline']
    language = prePrompt['original_prompt_language']
    need_to_re_scan = prePrompt['need_to_re_scan']

    if need_to_re_scan == "True":
        await controller.totalScan()

    await controller.update_tree()
    if pipeline == "0":
        await controller.explainer_task_pipeline(files, finalPrompt, language, role)
    elif pipeline == "1":
        await controller.code_format_pipeline(finalPrompt, role)
    elif pipeline == "2":
        await controller.fix_compile_error_pipeline(list(), role)  # add a missing parameter
    elif pipeline == "3":
        await controller.replace_code_pipeline(finalPrompt, role)
    elif pipeline == "4":
        await controller.add_files_folders_pipeline(finalPrompt, role)
    elif pipeline == "5":
        await controller.move_files_folders_pipeline(finalPrompt, role)
    elif pipeline == "6":
        await controller.light_code_task_pipeline(finalPrompt, role)
    elif pipeline == "7":
        await controller.regular_code_task_pipeline(finalPrompt, role)
    elif pipeline == "8":
        await controller.major_code_task_pipeline(finalPrompt, role)

    logger.info(f"Done work for: {user_prompt}")

if __name__ == "__main__":
    asyncio.run(main())