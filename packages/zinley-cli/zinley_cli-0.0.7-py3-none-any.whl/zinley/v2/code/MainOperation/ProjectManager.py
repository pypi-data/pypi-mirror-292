import os
import asyncio
import re
from pbxproj import XcodeProject
from pbxproj.pbxextensions import FileOptions
import shutil
from datetime import datetime
import string
import random
import subprocess

from zinley.v2.code.log.logger_config import get_logger
logger = get_logger(__name__)

class ProjectManager:
    def __init__(self, directory_path):
        self.directory_path = directory_path

    def get_current_time_formatted(self):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%m/%d/%y")
        return formatted_time

    async def create_and_add_file_to_xcodeproj(self, project_root_path, relative_path, file_name):
        try:
            # Check if the project root path exists
            if not os.path.exists(project_root_path):
                logger.info(f"The specified project root path {project_root_path} does not exist.")
                return

            if file_name == "":
                return

            # Construct the full path of the new file
            full_path = os.path.join(project_root_path, relative_path, file_name) if relative_path else os.path.join(project_root_path, file_name)
            app_name = relative_path.split('/')[0] if relative_path else 'UnknownApp'

            # Check if the file already exists
            if os.path.exists(full_path):
                logger.info(f"The file '{file_name}' already exists in {os.path.join(project_root_path, relative_path) if relative_path else project_root_path}. Skipping creation.")
                return

            # Create the file with content
            # file_content = f"""// \n//  {file_name} \n//  {app_name} \n// \n//  Created by Zinley on {self.get_current_time_formatted()} \n// \n"""
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as file:
                file.write(file_content)
            logger.info(f"File '{file_name}' created successfully in {os.path.join(project_root_path, relative_path) if relative_path else project_root_path}.")

            # Find the .xcodeproj file
            xcodeproj_path = next((os.path.join(project_root_path, item) for item in os.listdir(project_root_path) if item.endswith('.xcodeproj')), None)
            if not xcodeproj_path:
                logger.info(f"No .xcodeproj file found in {project_root_path}")
                return

            # Add the file to the Xcode project
            project = XcodeProject.load(os.path.join(xcodeproj_path, "project.pbxproj"))
            file_options = FileOptions(create_build_files=True)

            # Split relative path and navigate through each level
            parent_group = None
            if relative_path:
                path_parts = relative_path.split('/')
                parent_group = project.get_or_create_group(path_parts[0])
                for part in path_parts[1:]:
                    parent_group = project.get_or_create_group(part, parent=parent_group)

            added_files = project.add_file(full_path, file_options=file_options, force=False, parent=parent_group)
            project.save()
            logger.info(f"File '{file_name}' added to the Xcode project successfully.")

            return full_path
        except Exception as e:
            logger.info(f"Error creating and adding file: {e}")
            return None

    async def create_file_or_folder(self, project_root_path, relative_path, file_name):
        try:
            # Check if the project root path exists
            if not os.path.exists(project_root_path):
                logger.info(f"The specified project root path {project_root_path} does not exist.")
                return

            if file_name == "":
                return

            # Construct the full path of the new file
            full_path = os.path.join(project_root_path, relative_path, file_name) if relative_path else os.path.join(project_root_path, file_name)

            # Check if the file already exists
            if os.path.exists(full_path):
                logger.info(f"The file '{file_name}' already exists in {os.path.join(project_root_path, relative_path) if relative_path else project_root_path}. Skipping creation.")
                return

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            open(full_path, 'a').close()
            logger.info(f"File '{file_name}' created successfully in {os.path.join(project_root_path, relative_path) if relative_path else project_root_path}.")

            return full_path
        except Exception as e:
            logger.info(f"Error creating and adding file: {e}")
            return None

    async def move_file_within_xcodeproj(self, new_project_root_path, new_relative_path, file_name):
        try:
            # Check if the project root path exists
            if not os.path.exists(new_project_root_path):
                logger.info(f"The specified project root path {new_project_root_path} does not exist.")
                return

            # Find the existing file path
            existing_file_path = None
            for root, _, files in os.walk(new_project_root_path):
                if file_name in files:
                    existing_file_path = os.path.join(root, file_name)
                    break

            if not existing_file_path:
                logger.info(f"The file '{file_name}' does not exist in {new_project_root_path}.")
                return

            logger.info(f"Found existing file at: {existing_file_path}")

            # Construct the new full path of the file
            new_full_path = os.path.join(new_project_root_path, new_relative_path, file_name) if new_relative_path else os.path.join(new_project_root_path, file_name)
            logger.info(f"New file path will be: {new_full_path}")

            # Check if the new file path already exists
            if os.path.exists(new_full_path):
                logger.info(f"The file '{file_name}' already exists in {os.path.join(new_project_root_path, new_relative_path) if new_relative_path else new_project_root_path}. Skipping move.")
                return

            # Create new directory if it doesn't exist
            os.makedirs(os.path.dirname(new_full_path), exist_ok=True)

            # Move the file
            os.rename(existing_file_path, new_full_path)
            logger.info(f"File '{file_name}' moved successfully to {os.path.join(new_project_root_path, new_relative_path) if new_relative_path else new_project_root_path}.")

            # Find the .xcodeproj file
            xcodeproj_path = next((os.path.join(new_project_root_path, item) for item in os.listdir(new_project_root_path) if item.endswith('.xcodeproj')), None)
            if not xcodeproj_path:
                logger.info(f"No .xcodeproj file found in {new_project_root_path}")
                return

            logger.info(f"Found Xcode project at: {xcodeproj_path}")

            # Load the Xcode project
            project = XcodeProject.load(os.path.join(xcodeproj_path, "project.pbxproj"))
            file_options = FileOptions(create_build_files=True)

            # Remove the old file reference in the Xcode project
            existing_file_refs = project.get_files_by_path(existing_file_path)
            for file_ref in existing_file_refs:
                project.remove_file_by_id(file_ref.get_id())
                logger.info(f"Removed old file reference: {file_ref}")

            # Add the new file reference to the Xcode project
            parent_group = None
            if new_relative_path:
                path_parts = new_relative_path.split('/')
                parent_group = project.get_or_create_group(path_parts[0])
                for part in path_parts[1:]:
                    parent_group = project.get_or_create_group(part, parent=parent_group)
            else:
                parent_group = project.root_group

            project.add_file(new_full_path, file_options=file_options, force=False, parent=parent_group)
            project.save()
            logger.info(f"File '{file_name}' added to the Xcode project successfully in the new location: {new_full_path}")

            return new_full_path
        except Exception as e:
            logger.info(f"Error moving and adding file: {e}")
            return None

    async def move_file(self, new_project_root_path, new_relative_path, file_name):
        try:
            # Check if the project root path exists
            if not os.path.exists(new_project_root_path):
                logger.info(f"The specified project root path {new_project_root_path} does not exist.")
                return

            # Find the existing file path
            existing_file_path = None
            for root, _, files in os.walk(new_project_root_path):
                if file_name in files:
                    existing_file_path = os.path.join(root, file_name)
                    break

            if not existing_file_path:
                logger.info(f"The file '{file_name}' does not exist in {new_project_root_path}.")
                return

            logger.info(f"Found existing file at: {existing_file_path}")

            # Construct the new full path of the file
            new_full_path = os.path.join(new_project_root_path, new_relative_path, file_name) if new_relative_path else os.path.join(new_project_root_path, file_name)
            logger.info(f"New file path will be: {new_full_path}")

            # Check if the new file path already exists
            if os.path.exists(new_full_path):
                logger.info(f"The file '{file_name}' already exists in {os.path.join(new_project_root_path, new_relative_path) if new_relative_path else new_project_root_path}. Skipping move.")
                return

            # Create new directory if it doesn't exist
            os.makedirs(os.path.dirname(new_full_path), exist_ok=True)

            # Move the file
            os.rename(existing_file_path, new_full_path)
            logger.info(f"File '{file_name}' moved successfully to {os.path.join(new_project_root_path, new_relative_path) if new_relative_path else new_project_root_path}.")

            return new_full_path
        except Exception as e:
            logger.info(f"Error moving and adding file: {e}")
            return None


    async def execute_files_creation(self, instructions):
        for instruction in instructions:
            logger.info("---------------------------------------------------------------------------------------")
            try:
                logger.info(f"Executing Step {instruction['Title']} with pipeline {instruction['Pipeline']}")
            except:
                logger.info(f"Something wrong with instruction: {instruction}")

            parameters = instruction["Parameters"]
            function_name = instruction["Function_to_call"]
            pipeline = instruction["Pipeline"]
            if "create_and_add_file" in function_name:
                if pipeline == "1":
                    await self.create_and_add_file_to_xcodeproj(**parameters)
                elif pipeline == "2":
                    await self.create_file_or_folder(**parameters)
                else:
                    logger.info(f"Unknown creating pipeline: {pipeline}")
            elif "move_file" in function_name:
                if pipeline == "1":
                    await self.move_file_within_xcodeproj(**parameters)
                elif pipeline == "2":
                    await self.move_file(**parameters)
                else:
                    logger.info(f"Unknown moving pipeline: {pipeline}")
            else:
                logger.info(f"Unknown function: {function_name}")


# Usage example:
# manager = XcodeProjectManager("/path/to/project")
# asyncio.run(manager.execute_instructions(instructions))
