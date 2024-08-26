import os
import asyncio
import time
import subprocess
from concurrent.futures import ProcessPoolExecutor
from zinley.v2.code.Scanner1.ProjectScanner1 import \
    ProjectScanner1  # Ensure this module is correctly imported and available
from zinley.v2.code.explainer.ExplainerController import \
    ExplainerController  # Ensure this module is correctly imported and available
from zinley.v2.code.coding_agent.ControllerAgent import \
    ControllerAgent  # Ensure this module is correctly imported and available
import shutil  # Import shutil for copying directories
from zinley.v2.code.util.tree import Tree
import zinley.v2.code.util.utils as utils
import re
from FirstPromptAgent import FirstPromptAgent
import json

from zinley.v2.code.log.logger_config import get_logger

logger = get_logger(__name__)


def create_versioned_project_copy(project_path):
    try:
        # Extract the project name from the project_path
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        project_name = os.path.basename(project_path.rstrip("/"))

        # Define the base path for version control
        version_control_base_path = os.path.abspath(
            os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Version_control"))

        # Ensure the version control base path exists
        os.makedirs(version_control_base_path, exist_ok=True)

        # Create the project folder within the version control base path if it doesn't exist
        project_version_control_path = version_control_base_path
        os.makedirs(project_version_control_path, exist_ok=True)

        # List existing versions
        existing_versions = sorted([d for d in os.listdir(project_version_control_path) if
                                    os.path.isdir(os.path.join(project_version_control_path, d)) and d.startswith('v')],
                                   key=lambda x: int(x[1:]))

        # Determine the new version number
        if existing_versions:
            latest_version_number = int(existing_versions[-1][1:])
            new_version_number = latest_version_number + 1
        else:
            new_version_number = 1

        # Define the destination path for the new version
        new_version_path = os.path.join(project_version_control_path, f"v{new_version_number}")

        # Copy the entire project to the new version path
        shutil.copytree(project_path, new_version_path)
        logger.debug(f"Project copied to {new_version_path}")

        # Ensure only the two latest versions are kept
        if len(existing_versions) >= 2:
            oldest_version_path = os.path.join(project_version_control_path, existing_versions[0])
            shutil.rmtree(oldest_version_path)
            logger.debug(f"Deleted oldest version: {oldest_version_path}")

    except Exception as e:
        logger.error(f"An error occurred while copying the project: {e}")


def copy_project_with_version_control(project_path):
    try:
        # Extract the project name from the project_path
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        project_name = os.path.basename(project_path.rstrip("/"))

        # Define the base path for version control
        version_control_base_path = os.path.abspath(
            os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Version_control"))

        # Ensure the version control base path exists
        os.makedirs(version_control_base_path, exist_ok=True)

        # Create the project folder within the version control base path if it doesn't exist
        project_version_control_path = version_control_base_path

        # Determine the next version number
        existing_versions = sorted(
            [d for d in os.listdir(project_version_control_path) if
             os.path.isdir(os.path.join(project_version_control_path, d)) and d.startswith('v')],
            key=lambda x: int(x[1:]))

        version_numbers = [int(d[1:]) for d in existing_versions if d.startswith('v') and d[1:].isdigit()]
        next_version_number = max(version_numbers, default=0) + 1
        next_version = f"v{next_version_number}"

        # Define the destination path for the new version
        new_version_path = os.path.join(project_version_control_path, next_version)

        # Copy the entire project to the new version path
        shutil.copytree(project_path, new_version_path)

        logger.debug(f"Project copied to {new_version_path}")

        # Ensure only the two latest versions are kept
        if len(existing_versions) >= 2:
            oldest_version_path = os.path.join(project_version_control_path, existing_versions[0])
            shutil.rmtree(oldest_version_path)
            print(f"Deleted oldest version: {oldest_version_path}")

    except Exception as e:
        logger.error(f"An error occurred while copying the project: {e}")


def get_version_from_prompt(prompt):
    match = re.search(r'v\d+', prompt)
    if match:
        return match.group()
    else:
        raise ValueError("No version specified in the prompt")


def switch_project_version(project_path, version):
    # Extract the project name from the project_path
    home_directory = os.path.expanduser('~')
    hidden_zinley_folder_name = '.zinley'
    project_name = os.path.basename(project_path.rstrip("/"))

    # Define the base path for version control
    version_control_base_path = os.path.abspath(
        os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Version_control"))

    # Define the source path for the specified version
    version_path = os.path.join(version_control_base_path, version)

    # Check if the specified version exists
    if not os.path.exists(version_path):
        logger.debug(f"Version {version} does not exist")
        raise Exception(f"Version {version} does not exist")

    # Copy the entire version to the project path, overwriting existing files
    shutil.rmtree(project_path)
    shutil.copytree(version_path, project_path)

    logger.debug(f"Switched to {version} and updated the project at {project_path}")


async def start(project_path, api_key, max_tokens, endpoint, deployment_id, scheme):
    try:
        scanner = ProjectScanner1(project_path, api_key, endpoint, deployment_id, max_tokens)
        explainer_controller = ExplainerController(os.path.join(project_path), api_key, endpoint, deployment_id,
                                                   max_tokens)
        coding_controller = ControllerAgent(os.path.join(project_path), api_key, endpoint, deployment_id, max_tokens,
                                            scheme)
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = project_path.split('/')
        project_name = parts[-1]
        output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
        os.makedirs(output_dir, exist_ok=True)
        result_files_exist = os.path.exists(
            os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis",
                         "tree.txt"))
        file_modification_exist = os.path.exists(
            os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis",
                         "file_modification_times.txt"))

        if not result_files_exist or not file_modification_exist:
            logger.info("This project hasn't been scanned yet. I will scan it now!")
            start_time = time.time()
            await scanner.get_started()
            update_tree(project_path, home_directory, hidden_zinley_folder_name, project_name)
        else:
            logger.debug("Incremental scanning ...")
            # modified_files = utile
            scan_files = utils.get_new_or_modified_file(project_path)
            if scan_files:
                await scanner.get_incremental_scan_started(scan_files)
            else:
                logger.debug("No new or modified files to scan.")
            update_tree(project_path, home_directory, hidden_zinley_folder_name, project_name)

        while True:
            user_prompt_json = input("Enter your prompt (type 'exit' to quit): ")
            user_prompt, file_attachment = parse_payload(user_prompt_json, project_path, home_directory,
                                                         hidden_zinley_folder_name, project_name, scanner)
            if file_attachment:
                scan_files = utils.get_new_or_modified_file(project_path)
                if scan_files:
                    await scanner.get_incremental_scan_started(scan_files)
                    update_tree(project_path, home_directory, hidden_zinley_folder_name, project_name)


            result = await get_prePrompt(user_prompt, api_key, endpoint, deployment_id, max_tokens)
            pipeline = result['pipeline']
            if pipeline == "1":
                logger.debug(f"Zinley: Sent explaining request for: {user_prompt}")
                await explainer_controller.get_started(user_prompt)
            elif pipeline == "2":
                create_versioned_project_copy(project_path)
                logger.debug(f"Zinley: Sent coding request for: {user_prompt}")
                await coding_controller.get_started(user_prompt)
                logger.debug(f"Zinley: Done coding request for: {user_prompt}")
                copy_project_with_version_control(project_path)
                utils.create_file_modification_times(project_path)
            elif pipeline == "3":
                logger.debug(f"Zinley: Start scanning request now")
                await scan_request()
                utils.create_file_modification_times(project_path)
            elif pipeline == "4":
                try:
                    ver = get_version_from_prompt(user_prompt)
                    await switch_project_version(project_path, ver)
                    utils.create_file_modification_times(project_path)
                except ValueError:
                    ver = get_latest_version(project_path)
                    await switch_project_version(project_path, ver)
                    utils.create_file_modification_times(project_path)
                else:
                    logger.info(f"Version {ver} is not available")
            else:
                logger.info(f"Zinley: Exit now")
                break
    except Exception as e:
        logger.info(f"An error occurred while copying the project: {e}")
        user_prompt_json = input("Do you want to restore the previous version? (y/n): ")
        user_prompt, file_attachment = parse_payload(user_prompt_json, project_path)
        user_prompt = user_prompt.lower()

        if user_prompt == 'y' or user_prompt == "yes":
            switch_project_version(project_path, get_latest_version(project_path))
        else:
            exit()


async def scan_request():
    scanner = ProjectScanner1(project_path, api_key, endpoint, deployment_id, max_tokens)
    await scanner.get_started()


async def get_prePrompt(user_prompt, api_key, endpoint, deployment_id, max_tokens):
    first_prompt_controller = FirstPromptAgent(api_key, endpoint, deployment_id, max_tokens)
    """Generate idea plans based on user prompt and available files."""
    return await first_prompt_controller.get_prePrompt_plans(user_prompt)


def get_latest_version(project_path):
    home_directory = os.path.expanduser('~')
    hidden_zinley_folder_name = '.zinley'
    project_name = os.path.basename(project_path.rstrip("/"))

    # Define the base path for version control
    version_control_base_path = os.path.abspath(
        os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Version_control"))

    # Get all subdirectories in the version control base path
    subdirs = [d for d in os.listdir(version_control_base_path) if
               os.path.isdir(os.path.join(version_control_base_path, d))]

    # Filter out any directories that do not start with 'v'
    valid_subdirs = [d for d in subdirs if d.startswith('v')]

    # Get latest version
    latest_version = max(valid_subdirs, key=lambda x: int(x[1:]))

    return latest_version


def parse_payload(user_prompt_json, project_path, home_directory, hidden_zinley_folder_name, project_name,scanner):
    try:
        file_path = None
        data = json.loads(user_prompt_json)
        user_prompt = data.get("prompt", "")
        file_path = data.get("file_path", None)
        if file_path and os.path.exists(file_path):
            logger.info(f"{file_path} exists. Moving the file to {project_path}")
            # Check if the destination file already exists and remove it if necessary
            destination_file = os.path.join(project_path, os.path.basename(file_path))
            if os.path.exists(destination_file):
                os.remove(destination_file)
            shutil.move(file_path, project_path)
        else:
            file_path = None
    except json.JSONDecodeError:
        # If input is not valid JSON, treat it as plain text
        user_prompt = user_prompt_json
        logger.info(f"Received Plain Text Prompt: {user_prompt}")
    return user_prompt, file_path


def update_tree(project_path, home_directory, hidden_zinley_folder_name, project_name):
    parts = project_path.split('/')
    project_name = parts[-1]
    output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
    os.makedirs(output_dir, exist_ok=True)

    # Run the `tree` command and save the output to tree.txt, excluding the Zinley folder
    tree_path = os.path.join(output_dir, "tree.txt")

    # Clear the file contents before writing new content
    open(tree_path, 'w').close()

    with open(tree_path, 'w') as f:
        utils.tree(project_path, exclude="Zinley", stdout=f)

    # Need to update the all files modifying time
    utils.create_file_modification_times(project_path)


if __name__ == "__main__":
    project_path = user_prompt
    parts = project_path.split('/')
    scheme = parts[-1]
    api_key = os.getenv("OPENAI_API_KEY", "96ae909e40534d49a70c5e4bdfe54f62")
    endpoint = "https://zinley.openai.azure.com"
    deployment_id = "hi"
    max_tokens = 4096
    user_prompt_json = input("Enter your project path: ")
    user_prompt, file_attachment = parse_payload(user_prompt_json, project_path)
    asyncio.run(main(project_path, api_key, max_tokens, endpoint, deployment_id, scheme))
