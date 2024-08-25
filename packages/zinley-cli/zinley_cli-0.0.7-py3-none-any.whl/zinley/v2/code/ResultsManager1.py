import os
import json
import subprocess

from zinley.v2.code.util import utils

class ResultsManager1:
    def __init__(self):
        self.results = {}

    def update_dependencies_results(self, project_path, dependencies):
        """Overwrite the dependencies results with the new list of dependencies."""
        category = "dependencies"

        # Overwrite the dependencies result
        self.results[category] = dependencies

        # Save results to file immediately
        self.save_results_to_files(project_path)

    def update_total_results(self, project_path, file_path, summary):
        """Update results with the new file summary."""
        # Extract the file extension and filename
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lstrip('.')
        filename = os.path.basename(file_path)

        category = f"{file_extension}_files"

        # Check if the category exists, if not, create it
        if category not in self.results:
            self.results[category] = {}

        # Update the results with the new file or update the existing one
        self.results[category][filename] = summary

        # Save results to file immediately
        self.save_results_to_files(project_path)

    def update_results(self, project_path, file_path, summary):
        """Update results with the new file summary, comparing and updating only the changed parts."""
        # Extract the file extension and filename
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lstrip('.')
        filename = os.path.basename(file_path)

        category = f"{file_extension}_files"

        # Load existing results from file if they exist
        self.load_results_from_files(project_path)

        # Check if the category exists, if not, create it
        if category not in self.results:
            self.results[category] = {}

        # Update the results with the new file or update the existing one
        if filename in self.results[category]:
            # Compare and update only if the summary has changed
            if self.results[category][filename] != summary:
                self.results[category][filename] = summary
        else:
            self.results[category][filename] = summary

        # Save results to file immediately
        self.save_results_to_files(project_path)

    def save_results_to_files(self, project_path):
        """Save the current results to files."""
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = project_path.split('/')
        project_name = parts[-1]
        output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
        os.makedirs(output_dir, exist_ok=True)

        for category, data in self.results.items():
            file_path = os.path.join(output_dir, f"{category}_results.txt")
            with open(file_path, 'w') as f:
                f.write(json.dumps(data, indent=4))

        # Run the `tree` command and save the output to tree.txt, excluding the Zinley folder
        tree_path = os.path.join(output_dir, "tree.txt")
        with open(tree_path, 'w') as f:
            utils.tree(project_path, exclude="Zinley", stdout=f)

    def load_results_from_files(self, project_path):
        """Load results from files into the results dictionary."""
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = project_path.split('/')
        project_name = parts[-1]
        output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
        # output_dir = os.path.join(project_path, "Zinley", "Project_analysis")

        for file_name in os.listdir(output_dir):
            if file_name.endswith("_results.txt"):
                file_path = os.path.join(output_dir, file_name)
                category = file_name.replace("_results.txt", "")
                with open(file_path, 'r') as f:
                    self.results[category] = json.load(f)

    def save_milestones_to_files(self, project_path):
        """Alias for save_results_to_files for saving milestones."""
        self.save_results_to_files(project_path)

    def get_results(self):
        """Get the current results dictionary."""
        return self.results

    def clear_results(self):
        """Clear all results."""
        self.results = {}


class ResultsReader:
    def __init__(self, results_manager):
        self.results_manager = results_manager

    def read_results(self, category):
        """Read results for a given category."""
        return self.results_manager.get_results().get(category, None)


# Helper function to create dynamic result categories based on file extensions
def create_dynamic_results_manager(file_extensions):
    manager = ResultsManager1()
    for ext in file_extensions:
        manager.update_results(f"{ext}_files", {})
    return manager