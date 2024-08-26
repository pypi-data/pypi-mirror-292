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
from .PrePromptAgent import PrePromptAgent
from .FileLightWorkingAgent import FileLightWorkingAgent
from .LanguageAgent import LanguageAgent
from .TechnicalExplainerAgent import TechnicalExplainerAgent
from .LightCodeAgent import LightCodeAgent
from .TechStackAgent import TechStackAgent


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fsd.MainOperation.ProjectManager import ProjectManager
from fsd.MainOperation.ProjectsRunner import ProjectsRunner
from fsd.Scanner1.ProjectScanner1 import ProjectScanner1
from fsd.util import utils
from fsd.util.portkey import AIGateway
from fsd.log.logger_config import get_logger
logger = get_logger(__name__)

HOME_DIRECTORY = os.path.expanduser('~')
HIDDEN_ZINLEY_FOLDER = '.zinley'

class ControllerAgent:
    def __init__(self, directory_path, api_key, endpoint, deployment_id, max_tokens, scheme="Default"):
        part = directory_path.split('/')
        project_name = part[-1]
        self.directory_path = directory_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.scheme = scheme
        self.idea = IdeaDevelopment(os.path.join(directory_path), os.path.join(HOME_DIRECTORY, HIDDEN_ZINLEY_FOLDER, project_name, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.preprompt = PrePromptAgent(os.path.join(HOME_DIRECTORY, HIDDEN_ZINLEY_FOLDER, project_name, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.coder = CodingAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.project = ProjectManager(os.path.join(directory_path))
        self.runner = ProjectsRunner(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens, project_name)
        self.format = FormattingAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.lightCode = LightCodeAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.fileManager = FileManagerAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.fileFinder = FileFinderAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.lightWorkFinder = FileLightWorkingAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.lang = LanguageAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.techExplainer = TechnicalExplainerAgent(os.path.join(HOME_DIRECTORY, HIDDEN_ZINLEY_FOLDER, project_name, "Zinley/Project_analysis"), api_key, endpoint, deployment_id, max_tokens)
        self.scanner = ProjectScanner1(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)
        self.techStackAgent = TechStackAgent(os.path.join(directory_path), api_key, endpoint, deployment_id, max_tokens)


    def filter_non_asset_files(self, file_set):
        # Define a set of common asset file extensions
        asset_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',  # Image files
            '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv',    # Video files
            '.mp3', '.wav', '.aac', '.ogg', '.flac',            # Audio files
            '.svg', '.ico',                                     # Other common asset files
            '.webp', '.heic', '.m4v', '.mpg', '.mpeg'           # Additional formats
        }

        # Use a set comprehension to filter out asset files
        non_asset_files = {file for file in file_set if not any(file.endswith(ext) for ext in asset_extensions)}

        return non_asset_files

    def filter_non_asset_files_list(self, file_list):
        # Define a set of common asset file extensions
        asset_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',  # Image files
            '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv',    # Video files
            '.mp3', '.wav', '.aac', '.ogg', '.flac',            # Audio files
            '.svg', '.ico',                                     # Other common asset files
            '.webp', '.heic', '.m4v', '.mpg', '.mpeg'           # Additional formats
        }

        # Use a list comprehension to filter out asset files
        non_asset_files = [file for file in file_list if not any(file.endswith(ext) for ext in asset_extensions)]

        return non_asset_files

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
            logger.debug(f"Directory does not exist: {self.directory_path}")
            return None

        # Walk through the directory and look for the specified file
        for root, _, files in os.walk(self.directory_path):
            if filename in files:
                # Return the full path to the file if found
                return os.path.join(root, filename)

        # If the file wasn't found, print an error message and return None
        logger.debug(f"Couldn't find {filename} in: {self.directory_path}")
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

    async def run_requests(self, initial_instruction, request_list, role):
        """Run project requests."""
        return await self.runner.run_project(initial_instruction, request_list, role, self.scheme)

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
            main_path = self.scan_for_single_file(filename)
            result = await self.coder.get_coding_requests(is_first, title, filename, techStack)
            is_first = False
            title = result['Title']
            code = result['code']
            logger.info(f"Working on {filename}: {title}")
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
            all_fixing_files = await self.build_and_fix_compile_error(finalPrompt, working_files, role)
            logger.debug(f"all_fixing_files: {all_fixing_files}")
            all_final_files = set()
            all_final_files.update(working_files)
            all_final_files.update(all_fixing_files)
            logger.info(f"Formatting/refactoring phase done")
            if all_final_files:
                await self.scan_and_update(all_final_files)

    async def build_and_fix_compile_error(self, initial_instruction, file_list, role):
        """Build project and fix compile errors."""
        await self.update_tree()
        final_files = await self.run_requests(initial_instruction, file_list, role)
        return final_files

    async def fix_compile_error_pipeline(self, initial_instruction, file_list, role):
        """Pipeline for fixing compile errors."""
        logger.info("fix_compile_error_pipeline")
        final_files = await self.build_and_fix_compile_error(initial_instruction, file_list, role)
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
            user_prompt = input().lower()
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
        final_existing_files.update(os.path.basename(file) for file in new_adding_files)
        final_existing_files = self.filter_non_asset_files(final_existing_files)
        final_working_files = self.filter_non_asset_files(final_working_files)
        all_context = await self.build_existing_context(list(final_existing_files))
        totalfile = await self.get_coding_requests(idea_plan, list(final_working_files), all_context, context_files, role)
        logger.info(f"Next, I will build to check if any compile error was made")
        all_fixing_files = await self.build_and_fix_compile_error(idea_plan, totalfile, role)
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
            all_fixing_files = await self.build_and_fix_compile_error(finalPrompt, processed_files, role)
            logger.debug(f"all_fixing_files: {all_fixing_files}")
            all_final_files = set()
            all_final_files.update(processed_files)
            all_final_files.update(all_fixing_files)
            logger.info(f"Writting phase done")
            if all_final_files:
                logger.info(all_final_files)
                await self.scan_and_update(all_final_files)


    async def major_code_task_pipeline(self, finalPrompt, role):
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
            await self.fix_compile_error_pipeline("", list(), role)  # add a missing parameter
        elif pipeline == "2":
            await self.add_files_folders_pipeline(finalPrompt, role)
        elif pipeline == "3":
            await self.move_files_folders_pipeline(finalPrompt, role)
        elif pipeline == "4":
            await self.light_code_task_pipeline(finalPrompt, role)
        elif pipeline == "5":
            await self.regular_code_task_pipeline(finalPrompt, role)

        logger.info(f"Done work for: {user_prompt}")
