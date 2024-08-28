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
from typing import List, Dict, Optional

from fsd.log.logger_config import get_logger
logger = get_logger(__name__)

class ProjectManager:
    def __init__(self, directory_path: str):
        self.directory_path = directory_path

    @staticmethod
    def get_current_time_formatted() -> str:
        return datetime.now().strftime("%m/%d/%y")

    async def create_and_add_file_to_xcodeproj(self, project_root_path: str, relative_path: str, file_name: str) -> Optional[str]:
        if not self._validate_inputs(project_root_path, file_name):
            return None

        full_path = self._construct_full_path(project_root_path, relative_path, file_name)
        app_name = self._extract_app_name(relative_path)

        if os.path.exists(full_path):
            logger.info(f"File '{file_name}' already exists in {os.path.dirname(full_path)}. Skipping creation.")
            return None

        self._create_file_with_content(full_path, app_name)
        xcodeproj_path = self._find_xcodeproj(project_root_path)

        if not xcodeproj_path:
            logger.info(f"No .xcodeproj file found in {project_root_path}")
            return None

        self._add_file_to_xcode_project(xcodeproj_path, full_path, relative_path)
        return full_path

    async def create_file_or_folder(self, project_root_path: str, relative_path: str, file_name: str) -> Optional[str]:
        if not self._validate_inputs(project_root_path, file_name):
            return None

        full_path = self._construct_full_path(project_root_path, relative_path, file_name)

        if os.path.exists(full_path):
            logger.info(f"File '{file_name}' already exists in {os.path.dirname(full_path)}. Skipping creation.")
            return None

        self._create_empty_file(full_path)
        return full_path

    async def move_file_within_xcodeproj(self, new_project_root_path: str, new_relative_path: str, file_name: str) -> Optional[str]:
        if not self._validate_inputs(new_project_root_path, file_name):
            return None

        existing_file_path = self._find_existing_file(new_project_root_path, file_name)
        if not existing_file_path:
            return None

        new_full_path = self._construct_full_path(new_project_root_path, new_relative_path, file_name)
        if os.path.exists(new_full_path):
            logger.info(f"File '{file_name}' already exists in {os.path.dirname(new_full_path)}. Skipping move.")
            return None

        self._move_file(existing_file_path, new_full_path)
        xcodeproj_path = self._find_xcodeproj(new_project_root_path)

        if not xcodeproj_path:
            logger.info(f"No .xcodeproj file found in {new_project_root_path}")
            return None

        self._update_xcode_project(xcodeproj_path, existing_file_path, new_full_path, new_relative_path)
        return new_full_path

    async def move_file(self, new_project_root_path: str, new_relative_path: str, file_name: str) -> Optional[str]:
        if not self._validate_inputs(new_project_root_path, file_name):
            return None

        existing_file_path = self._find_existing_file(new_project_root_path, file_name)
        if not existing_file_path:
            return None

        new_full_path = self._construct_full_path(new_project_root_path, new_relative_path, file_name)
        if os.path.exists(new_full_path):
            logger.info(f"File '{file_name}' already exists in {os.path.dirname(new_full_path)}. Skipping move.")
            return None

        self._move_file(existing_file_path, new_full_path)
        return new_full_path

    async def execute_files_creation(self, instructions: List[Dict]) -> None:
        for instruction in instructions:
            logger.info("-" * 87)
            self._log_instruction(instruction)

            parameters = instruction["Parameters"]
            function_name = instruction["Function_to_call"]
            pipeline = instruction["Pipeline"]

            await self._execute_instruction(function_name, pipeline, parameters)

    def _validate_inputs(self, project_root_path: str, file_name: str) -> bool:
        if not os.path.exists(project_root_path):
            logger.info(f"The specified project root path {project_root_path} does not exist.")
            return False
        if not file_name:
            logger.info("File name is empty.")
            return False
        return True

    @staticmethod
    def _construct_full_path(project_root_path: str, relative_path: str, file_name: str) -> str:
        return os.path.join(project_root_path, relative_path, file_name) if relative_path else os.path.join(project_root_path, file_name)

    @staticmethod
    def _extract_app_name(relative_path: str) -> str:
        return relative_path.split('/')[0] if relative_path else 'UnknownApp'

    def _create_file_with_content(self, full_path: str, app_name: str) -> None:
        file_content = f"""// \n//  {os.path.basename(full_path)} \n//  {app_name} \n// \n//  Created by Zinley on {self.get_current_time_formatted()} \n// \n"""
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as file:
            file.write(file_content)
        logger.info(f"File '{os.path.basename(full_path)}' created successfully in {os.path.dirname(full_path)}.")

    @staticmethod
    def _find_xcodeproj(project_root_path: str) -> Optional[str]:
        return next((os.path.join(project_root_path, item) for item in os.listdir(project_root_path) if item.endswith('.xcodeproj')), None)

    def _add_file_to_xcode_project(self, xcodeproj_path: str, full_path: str, relative_path: str) -> None:
        project = XcodeProject.load(os.path.join(xcodeproj_path, "project.pbxproj"))
        file_options = FileOptions(create_build_files=True)

        parent_group = self._get_or_create_groups(project, relative_path)

        project.add_file(full_path, file_options=file_options, force=False, parent=parent_group)
        project.save()
        logger.info(f"File '{os.path.basename(full_path)}' added to the Xcode project successfully.")

    @staticmethod
    def _get_or_create_groups(project: XcodeProject, relative_path: str) -> Optional[object]:
        if not relative_path:
            return None
        parent_group = project.get_or_create_group(relative_path.split('/')[0])
        for part in relative_path.split('/')[1:]:
            parent_group = project.get_or_create_group(part, parent=parent_group)
        return parent_group

    def _create_empty_file(self, full_path: str) -> None:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        open(full_path, 'a').close()
        logger.info(f"File '{os.path.basename(full_path)}' created successfully in {os.path.dirname(full_path)}.")

    @staticmethod
    def _find_existing_file(project_root_path: str, file_name: str) -> Optional[str]:
        for root, _, files in os.walk(project_root_path):
            if file_name in files:
                return os.path.join(root, file_name)
        logger.info(f"The file '{file_name}' does not exist in {project_root_path}.")
        return None

    def _move_file(self, existing_file_path: str, new_full_path: str) -> None:
        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
        os.rename(existing_file_path, new_full_path)
        logger.info(f"File '{os.path.basename(new_full_path)}' moved successfully to {os.path.dirname(new_full_path)}.")

    def _update_xcode_project(self, xcodeproj_path: str, existing_file_path: str, new_full_path: str, new_relative_path: str) -> None:
        project = XcodeProject.load(os.path.join(xcodeproj_path, "project.pbxproj"))
        file_options = FileOptions(create_build_files=True)

        existing_file_refs = project.get_files_by_path(existing_file_path)
        for file_ref in existing_file_refs:
            project.remove_file_by_id(file_ref.get_id())
            logger.info(f"Removed old file reference: {file_ref}")

        parent_group = self._get_or_create_groups(project, new_relative_path) or project.root_group

        project.add_file(new_full_path, file_options=file_options, force=False, parent=parent_group)
        project.save()
        logger.info(f"File '{os.path.basename(new_full_path)}' added to the Xcode project successfully in the new location: {new_full_path}")

    @staticmethod
    def _log_instruction(instruction: Dict) -> None:
        try:
            logger.info(f"Executing Step {instruction['Title']} with pipeline {instruction['Pipeline']}")
        except KeyError:
            logger.info(f"Something wrong with instruction: {instruction}")

    async def _execute_instruction(self, function_name: str, pipeline: str, parameters: Dict) -> None:
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
