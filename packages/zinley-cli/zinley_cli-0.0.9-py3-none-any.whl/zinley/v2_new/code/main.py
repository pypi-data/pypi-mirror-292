import os
import asyncio
import time
import subprocess
from concurrent.futures import ProcessPoolExecutor
from zinley.v2_new.code.Scanner1.ProjectScanner1 import ProjectScanner1  # Ensure this module is correctly imported and available
from zinley.v2_new.code.explainer.ExplainerController import ExplainerController  # Ensure this module is correctly imported and available
from zinley.v2_new.code.coding_agent.ControllerAgent import ControllerAgent  # Ensure this module is correctly imported and available
import shutil  # Import shutil for copying directories
import zinley.v2_new.code.util.utils as utils
import re
from FirstPromptAgent import FirstPromptAgent


def create_versioned_project_copy(project_path):
    try:
        # Extract the project name from the project_path
        project_name = os.path.basename(project_path.rstrip("/"))

        # Define the base path for version control
        version_control_base_path = os.path.abspath(os.path.join(project_path, "../../Version_control"))

        # Ensure the version control base path exists
        os.makedirs(version_control_base_path, exist_ok=True)

        # Create the project folder within the version control base path if it doesn't exist
        project_version_control_path = os.path.join(version_control_base_path, project_name)
        os.makedirs(project_version_control_path, exist_ok=True)

        # Determine if v1 exists
        v1_path = os.path.join(project_version_control_path, "v1")

        # Check if v1 is empty or doesn't exist
        if not os.path.exists(v1_path) or not os.listdir(v1_path):
            # Define the destination path for the new version
            new_version_path = v1_path if not os.path.exists(v1_path) else None

            # Copy the entire project to the new version path if it is empty or doesn't exist
            if new_version_path:
                shutil.copytree(project_path, new_version_path)
                print(f"Project copied to {new_version_path}")
            else:
                print(f"v1 already exists and is not empty, skipping copy.")
        else:
            print(f"v1 already exists and is not empty, skipping copy.")
    except Exception as e:
        print(f"An error occurred while copying the project: {e}")


def copy_project_with_version_control(project_path):
    try:
        # Extract the project name from the project_path
        project_name = os.path.basename(project_path.rstrip("/"))

        # Define the base path for version control
        version_control_base_path = os.path.abspath(os.path.join(project_path, "../../Version_control"))

        # Ensure the version control base path exists
        os.makedirs(version_control_base_path, exist_ok=True)

        # Create the project folder within the version control base path if it doesn't exist
        project_version_control_path = os.path.join(version_control_base_path, project_name)
        os.makedirs(project_version_control_path, exist_ok=True)

        # Determine the next version number
        existing_versions = [d for d in os.listdir(project_version_control_path) if
                             os.path.isdir(os.path.join(project_version_control_path, d))]
        version_numbers = [int(d[1:]) for d in existing_versions if d.startswith('v') and d[1:].isdigit()]
        next_version_number = max(version_numbers, default=0) + 1
        next_version = f"v{next_version_number}"

        # Define the destination path for the new version
        new_version_path = os.path.join(project_version_control_path, next_version)

        # Copy the entire project to the new version path
        shutil.copytree(project_path, new_version_path)

        print(f"Project copied to {new_version_path}")
    except Exception as e:
        print(f"An error occurred while copying the project: {e}")


def get_version_from_prompt(prompt):
    match = re.search(r'v\d+', prompt)
    if match:
        return match.group()
    else:
        raise ValueError("No version specified in the prompt")


def switch_project_version(project_path, version):
    # Extract the project name from the project_path
    project_name = os.path.basename(project_path.rstrip("/"))

    # Define the base path for version control
    version_control_base_path = os.path.abspath(os.path.join(project_path, "../../Version_control"))

    # Define the source path for the specified version
    version_path = os.path.join(version_control_base_path, project_name, version)

    # Check if the specified version exists
    if not os.path.exists(version_path):
        print(f"Version {version} does not exist")
        return

    # Copy the entire version to the project path, overwriting existing files
    shutil.rmtree(project_path)
    shutil.copytree(version_path, project_path)

    print(f"Switched to {version} and updated the project at {project_path}")


async def start(project_path, api_key, max_tokens, endpoint, deployment_id, schema):
    scanner = ProjectScanner1(project_path, api_key, endpoint, deployment_id, max_tokens)
    explainer_controller = ExplainerController(os.path.join(project_path), api_key, endpoint, deployment_id, max_tokens)
    coding_controller = ControllerAgent("iOS developer", os.path.join(project_path), api_key, endpoint, deployment_id,
                                        max_tokens, schema)

    result_files_exist = os.path.exists(os.path.join(project_path, "Zinley", "Project_analysis", "tree.txt"))
    file_modification_exist = os.path.exists(os.path.join(project_path, "Zinley", "Project_analysis", "tree.txt"))

    if not result_files_exist or not file_modification_exist:
        print("This project hasn't been scanned yet. I will scan it now!")
        start_time = time.time()
        await scanner.get_started()
    else:
        print("Incremental scanning ...")
        # modified_files = utile
        scan_files = utils.get_new_or_modified_file(project_path)
        if scan_files:
            await scanner.get_incremental_scan_started(scan_files)
        else:
            print("No new or modified files to scan.")
        output_dir = os.path.join(project_path, "Zinley", "Project_analysis")
        os.makedirs(output_dir, exist_ok=True)

        # Run the `tree` command and save the output to tree.txt, excluding the Zinley folder
        tree_path = os.path.join(output_dir, "tree.txt")

        # Clear the file contents before writing new content
        open(tree_path, 'w').close()

        with open(tree_path, 'w') as f:
            subprocess.run(['tree', project_path, '-I', 'Zinley'], stdout=f, text=True)

    # Need to update the all files modifying time
    utils.create_file_modification_times(project_path)

    while True:
        user_prompt = input("Enter your prompt (type 'exit' to quit): ")
        result = await get_prePrompt(user_prompt, api_key, endpoint, deployment_id, max_tokens)
        pipeline = result['pipeline']
        if pipeline == "1":
            print(f"Zinley: Sent explaining request for: {user_prompt}")
            await explainer_controller.get_started(user_prompt)
        elif pipeline == "2":
            create_versioned_project_copy(project_path)
            print(f"Zinley: Sent coding request for: {user_prompt}")
            await coding_controller.get_started(user_prompt)
            print(f"Zinley: Done coding request for: {user_prompt}")
            copy_project_with_version_control(project_path)
            utils.create_file_modification_times(project_path)
        elif pipeline == "3":
            print(f"Zinley: Start scanning request now")
            await scan_request()
            utils.create_file_modification_times(project_path)
        elif pipeline == "4":
            print(f"Zinley: Exit now")
            break


async def scan_request():
    scanner = ProjectScanner1(project_path, api_key, endpoint, deployment_id, max_tokens)
    await scanner.get_started()


async def get_prePrompt(user_prompt, api_key, endpoint, deployment_id, max_tokens):
    first_prompt_controller = FirstPromptAgent(api_key, endpoint, deployment_id, max_tokens)
    """Generate idea plans based on user prompt and available files."""
    return await first_prompt_controller.get_prePrompt_plans(user_prompt)


if __name__ == "__main__":
    project_path = user_prompt = input("Enter your project path: ")
    parts = project_path.split('/')
    schema = parts[-1]
    api_key = os.getenv("OPENAI_API_KEY", "96ae909e40534d49a70c5e4bdfe54f62")
    endpoint = "https://zinley.openai.azure.com"
    deployment_id = "hi"
    max_tokens = 4096

    asyncio.run(main(project_path, api_key, max_tokens, endpoint, deployment_id, schema))
