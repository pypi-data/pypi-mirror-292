import os
import asyncio
import time
import subprocess
from concurrent.futures import ProcessPoolExecutor
from scanner.ProjectScanner import ProjectScanner  # Ensure this module is correctly imported and available
from explainer.ExplainerController import ExplainerController  # Ensure this module is correctly imported and available
from ResultsManager import ResultsManager, ResultsReader  # Import the required classes
from coding_agent.ControllerAgent import ControllerAgent  # Ensure this module is correctly imported and available
import shutil  # Import shutil for copying directories
import re
from FirstPromptAgent import FirstPromptAgent

async def analyze_all(scanner, results_manager):
    tasks = {
        "images": scanner.analyze_project_images(),
        "nib_files": scanner.analyze_nib_files(),
        "storyboard_files": scanner.analyze_storyboard_files(),
        "objc_files": scanner.analyze_objc_files(),
        "plist_files": scanner.analyze_plist_files(),
        "swift_files": scanner.analyze_swift_files()
    }

    tasks_list = [analyze_task(category, task, results_manager) for category, task in tasks.items()]

    await asyncio.gather(*tasks_list)

async def analyze_task(category, task, results_manager):
    try:
        print(f"Starting analysis of {category}...")
        results = await task
        results_manager.update_results(category, results)
        print(f"Completed analysis of {category}")
    except Exception as e:
        print(f"Error processing {category}: {e}")

def analyze_project(scanner):
    return scanner.analyze_project()

def copy_project_with_version_control(project_path):
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
    existing_versions = [d for d in os.listdir(project_version_control_path) if os.path.isdir(os.path.join(project_version_control_path, d))]
    version_numbers = [int(d[1:]) for d in existing_versions if d.startswith('v') and d[1:].isdigit()]
    next_version_number = max(version_numbers, default=0) + 1
    next_version = f"v{next_version_number}"

    # Define the destination path for the new version
    new_version_path = os.path.join(project_version_control_path, next_version)

    # Copy the entire project to the new version path
    shutil.copytree(project_path, new_version_path)

    print(f"Project copied to {new_version_path}")

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

async def main(project_path, api_key, max_tokens, endpoint, deployment_id):
    scanner = ProjectScanner(project_path, api_key, endpoint, deployment_id, max_tokens)
    explainer_controller = ExplainerController("../projects/DemoApp", api_key, endpoint, deployment_id, max_tokens)
    coding_controller = ControllerAgent("../projects/DemoApp", api_key, endpoint, deployment_id, max_tokens)
    results_manager = ResultsManager()
    results_reader = ResultsReader(results_manager)  # Instantiate ResultsReader

    result_files_exist = os.path.exists(os.path.join(project_path, "Zinley", "Project_analysis", "project_overall_description.txt"))

    if not result_files_exist:
        print("This project hasn't been scanned yet. I will scan it now!")
        skip_scanner = 'n'
    else:
        print("This project has been scanned. However, please note, if you modify the code yourself, you should let us scan again to stay up to date.")
        skip_scanner = input("Do you want to skip the scanner part? (y/n): ").strip().lower()

    if skip_scanner == 'n':
        print("Starting project analysis...")
        start_time = time.time()
        results_manager.clear_results()
        await analyze_all(scanner, results_manager)

        with ProcessPoolExecutor() as executor:
            future = executor.submit(analyze_project, scanner)
            analysis = future.result()

        end_time = time.time()
        runtime = end_time - start_time

        results_manager.save_results_to_files(project_path, analysis)

        print(f"Total runtime: {runtime:.2f} seconds")
    else:
        print("Skipping scanner part...")
        results_manager.load_results_from_files(project_path)

        # Print the loaded results
        loaded_results = results_manager.get_results()

        with ProcessPoolExecutor() as executor:
            future = executor.submit(analyze_project, scanner)
            analysis = future.result()

        output_dir = os.path.join(project_path, "Zinley", "Project_analysis")
        os.makedirs(output_dir, exist_ok=True)

        project_overall_description = (
            f"Project Type: {analysis['project_type']}\n"
            f"Storyboard Percentage: {analysis['storyboard_percentage']:.2f}%\n"
            f"SwiftUI Percentage: {analysis['swiftui_percentage']:.2f}%\n"
            f"XIB Percentage: {analysis['xib_percentage']:.2f}%\n"
            f"NIB Percentage: {analysis['nib_percentage']:.2f}%\n"
            f"Objective-C Percentage: {analysis['objc_percentage']:.2f}%\n"
        )

        overall_desc_path = os.path.join(output_dir, "project_overall_description.txt")
        with open(overall_desc_path, 'w') as f:
            f.write(project_overall_description)

        # Run the `tree` command and save the output to tree.txt, excluding the Zinley folder
        tree_path = os.path.join(output_dir, "tree.txt")

        # Clear the file contents before writing new content
        open(tree_path, 'w').close()

        with open(tree_path, 'w') as f:
            subprocess.run(['tree', project_path, '-I', 'Zinley'], stdout=f, text=True)

    while True:
        user_prompt = input("Enter your prompt (type 'exit' to quit): ")
        result = await get_prePrompt(user_prompt)
        pipeline = result['pipeline']
        if pipeline == "1":
            print(f"Zinley: Sent explaining request for: {user_prompt}")
            await explainer_controller.get_started(user_prompt)
        elif pipeline == "2":
            print(f"Zinley: Sent coding request for: {user_prompt}")
            await coding_controller.get_started(user_prompt)
            print(f"Zinley: Done coding request for: {user_prompt}")
            copy_project_with_version_control(project_path)
        elif pipeline == "3":
            print(f"Zinley: Start scanning request now")
            await scan_request()
        elif pipeline == "4":
            print(f"Zinley: Exit now")
            break

async def scan_request():
    scanner = ProjectScanner(project_path, api_key, endpoint, deployment_id, max_tokens)
    results_manager = ResultsManager()
    results_reader = ResultsReader(results_manager)  # Instantiate ResultsReader
    print("Select categories to scan (e.g., 1,2,3):")
    print("1: All")
    print("2: Images")
    print("3: Nib Files")
    print("4: Storyboard Files")
    print("5: ObjC Files")
    print("6: Plist Files")
    print("7: Swift Files")
    category_selection = input("Enter your selection: ").strip().split(',')
    start_scan_time = time.time()
    categories_map = {
        "1": "all",
        "2": "images",
        "3": "nib_files",
        "4": "storyboard_files",
        "5": "objc_files",
        "6": "plist_files",
        "7": "swift_files"
    }

    categories = [categories_map.get(selection.strip()) for selection in category_selection]

    if "all" in categories:
        results_manager.clear_results()
        await analyze_all(scanner, results_manager)
    else:
        results_manager.clear_results()
        scan_tasks = []
        for category in categories:
            if category:
                task = {
                    "images": scanner.analyze_project_images,
                    "nib_files": scanner.analyze_nib_files,
                    "storyboard_files": scanner.analyze_storyboard_files,
                    "objc_files": scanner.analyze_objc_files,
                    "plist_files": scanner.analyze_plist_files,
                    "swift_files": scanner.analyze_swift_files
                }.get(category)

                if task:
                    scan_tasks.append(analyze_task(category, task(), results_manager))
                else:
                    print(f"Unknown scan category: {category}")

        await asyncio.gather(*scan_tasks)
        # Save the results after scanning
    with ProcessPoolExecutor() as executor:
        future = executor.submit(analyze_project, scanner)
        analysis = future.result()

    end_scan_time = time.time()
    run_scan_time = end_scan_time - start_scan_time
    print(f"Total runtime: {run_scan_time:.2f} seconds")
    results_manager.save_results_to_files(project_path, analysis)

async def get_prePrompt(user_prompt):
    first_prompt_controller = FirstPromptAgent(api_key, endpoint, deployment_id, max_tokens)
    """Generate idea plans based on user prompt and available files."""
    return await first_prompt_controller.get_prePrompt_plans(user_prompt)

if __name__ == "__main__":
    project_path = "../projects/DemoApp"
    api_key = os.getenv("OPENAI_API_KEY", "96ae909e40534d49a70c5e4bdfe54f62")
    endpoint = "https://zinley.openai.azure.com"
    deployment_id = "gpt-4o"
    max_tokens = 4096

    asyncio.run(main(project_path, api_key, max_tokens, endpoint, deployment_id))
