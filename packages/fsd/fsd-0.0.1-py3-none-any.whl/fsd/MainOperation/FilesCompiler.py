from abc import ABC, abstractmethod
from enum import Enum
import subprocess
import os
import aiohttp
import asyncio
import json
import sys
import time
import requests
import re

from log.logger_config import get_logger
from util import utils

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from coding_agent.SelfHealingAgent import SelfHealingAgent
from coding_agent.FileManagerAgent import FileManagerAgent
from coding_agent.BugExplainer import BugExplainer
from coding_agent.BugExplorer import BugExplorer
from util.utils import get_preferred_simulator_uuid
from util.utils import get_current_time_formatted
from .ProjectManager import ProjectManager
from .MainBuilderAgent import MainBuilderAgent

logger = get_logger(__name__)


# Enum for Compiler Types
class CompilerType(Enum):
    PYTHON = "python"
    JAVA = "java"
    GO = "go"


# Abstract Compiler class
class Compiler(ABC):
    def __init__(self, basename, role, directory_path, api_key, endpoint, deployment_id, max_tokens, scheme, commands,
                 max_retries=10):
        self.directory = directory_path
        self.basename = basename
        self.role = role
        self.max_retries = max_retries
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.scheme = scheme
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.self_healing = SelfHealingAgent(directory_path, api_key, endpoint, deployment_id, max_tokens)
        self.bugExplainer = BugExplainer(directory_path, api_key, endpoint, deployment_id, max_tokens)
        self.bugExplorer = BugExplorer(directory_path, api_key, endpoint, deployment_id, max_tokens)
        self.project = ProjectManager(directory_path)
        self.fileManager = FileManagerAgent(directory_path, api_key, endpoint, deployment_id, max_tokens)
        self.builderAgent = MainBuilderAgent(directory_path, api_key, endpoint, deployment_id, max_tokens)
        self.commands = commands

    @abstractmethod
    def compile_and_run(self):
        pass

    def scan_txt_files(self, path):
        """
        Scan for 'tree.txt' in the specified directory.

        Returns:
            list: Path to 'tree.txt' if found, else an empty list.
        """
        txt_files = []

        if not os.path.exists(path):
            logger.debug(f"Directory does not exist: {path}")
            return txt_files

        for root, dirs, files in os.walk(path):
            for file in files:
                if file == 'tree.txt':
                    file_path = os.path.join(root, file)
                    txt_files.append(file_path)
                    # Assuming you want to stop after finding the first 'tree.txt'
                    return txt_files

        return txt_files

    def read_txt_files(self, files):
        """
        Get development plans for a list of txt files from OpenAI based on user prompt.

        Args:
            files (list): List of file paths.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """
        all_file_contents = ""

        for file_path in files:
            file_content = self.read_file_content(file_path)
            if file_content:
                all_file_contents += f"\n\nFile: {file_path}\n{file_content}"

        return all_file_contents

    def read_file_content(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            logger.info(f"Failed to read file {file_path}: {e}")
            return None

    def log_errors(self, log_file_path):
        error_lines = []
        damaged_files = set()
        error_details = []

        # Regular expression to match file path and error line details
        error_regex = re.compile(r'(/[^:]+\.swift):(\d+):(\d+): error: (.+)')

        with open(log_file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if "error:" in line.lower():
                error_lines.append(line)
                match = error_regex.search(line)
                if match:
                    full_file_path = match.group(1)
                    file_name = os.path.basename(full_file_path)  # Extract the filename
                    line_number = int(match.group(2))
                    column_number = int(match.group(3))
                    error_message = match.group(4)

                    damaged_files.add(file_name)

                    # Read the damaged file to get the specific line with the error
                    try:
                        with open(full_file_path, 'r') as swift_file:
                            swift_lines = swift_file.readlines()

                        if line_number <= len(swift_lines):
                            damaged_code = swift_lines[line_number - 1].strip()
                        else:
                            damaged_code = "Line number exceeds file length."

                        # Get additional context around the error line
                        error_details.append({
                            'file': file_name,
                            'line': line_number,
                            'column': column_number,
                            'message': error_message,
                            'code': damaged_code
                        })
                    except FileNotFoundError:
                        error_details.append({
                            'file': file_name,
                            'line': line_number,
                            'column': column_number,
                            'message': error_message,
                            'code': "File not found."
                        })
                else:
                    # If the error couldn't be parsed, add the original line
                    error_details.append({
                        'file': 'unknown',
                        'line': 'unknown',
                        'column': 'unknown',
                        'message': line.strip(),
                        'code': 'N/A'
                    })

        with open('bug_logs.txt', 'w') as output_file:
            for error in error_details:
                output_file.write(
                    f"Damaged code: {error['code']} - Error: {error['message']} - File path: {error['file']}\n")
                output_file.write("\n" + "-" * 80 + "\n\n")  # Adds a separator between errors

        damaged_files_list = list(damaged_files)  # Convert set to list before returning

        logger.info(f"All error lines have been logged. {damaged_files_list}")

        return damaged_files_list

    async def get_file_planning(self, idea_plan, tree):
        """Generate idea plans based on user prompt and available files."""
        return await self.fileManager.get_file_plannings(idea_plan, tree)

    async def process_creation(self, data):
        # Check if 'Is_creating' is True
        if data.get('Is_creating'):
            # Extract the processes array
            processes = data.get('Adding_new_files', [])
            # Create a list of process details
            await self.project.execute_files_creation(processes)
            await self.update_tree()
        else:
            logger.info("No new file to be added.")

    async def get_tree_txt_files(self):
        """
        Scan for tree.txt files in the specified directory.

        Returns:
            list: Paths to all tree.txt files.
        """
        await self.update_tree()
        tree_txt_files = []
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = self.directory.split('/')
        project_name = parts[-1]
        tree_path = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
        # tree_path = self.directory_path + "/Zinley/Project_analysis"

        if not os.path.exists(tree_path):
            logger.debug(f"Directory does not exist: {tree_path}")
            return tree_txt_files

        for root, dirs, files in os.walk(tree_path):
            for file in files:
                if file == 'tree.txt':
                    file_path = os.path.join(root, file)
                    tree_txt_files.append(file_path)

        return tree_txt_files

    async def update_tree(self):
        """Update the project directory tree and save to tree.txt."""
        tree_path = self.directory
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = tree_path.split('/')
        project_name = parts[-1]
        output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
        os.makedirs(output_dir, exist_ok=True)
        tree_file_path = os.path.join(output_dir, "tree.txt")
        # Open the file to write the tree output
        with open(tree_file_path, 'w') as f:
            utils.tree(self.directory, exclude="Zinley", stdout=f)


# ======================================================

class PythonCompiler(Compiler):
    async def compile_and_run(self):
        if not self.basename:
            return []
        logger.info(f"Executing Python file: {self.directory}")
        project_directory = os.path.expanduser(self.directory)
        logger.info(f"Building project at: {project_directory}")
        os.chdir(project_directory)
        totalfile = set()
        fixing_related_files = set()

        bug_log_path = os.path.join(project_directory, 'bug_logs.txt')
        retries = 0
        cleaned = False

        home_directory = os.path.expanduser('~')
        hidden_zinley_fold_name = '.zinley'
        parts = self.directory.split('/')
        project_name = parts[-1]

        txt_files = self.scan_txt_files(
            os.path.join(home_directory, hidden_zinley_fold_name, project_name, 'Zinley/Project_analysis'))
        executed_commands = set()
        while retries < self.max_retries:
            self.self_healing.clear_conversation_history()
            self.bugExplorer.clear_conversation_history()

            self.bugExplorer.initial_setup("", self.role)
            self.self_healing.initial_setup(self.role)
            error_flag = False
            for command in self.commands:
                if command in executed_commands:
                    continue
                try:
                    logger.debug(f"Running {command}")
                    command_parts = command.split()
                    if "requirement" in command and os.path.exists(command_parts[-1]):
                        result = subprocess.run(command_parts, timeout=120, capture_output=True, text=True, check=True)
                    else:
                        result = subprocess.run(command_parts, timeout=5, capture_output=True, text=True, check=True)
                    logger.debug(f"This is the {result}")
                    executed_commands.add(command)
                except subprocess.TimeoutExpired:
                    error_flag = True
                    logger.debug("The process of executing python file exceeded the time limit, but it's not treated "
                                 "make an error.")
                    retries += 1
                    executed_commands.add(command)
                    continue
                except subprocess.CalledProcessError as e:
                    error_flag = True
                    logger.info("Oops! Something went wrong, I will work on the fix right now.")
                    bug_log_content = e.stdout if e.stdout else "\n"
                    bug_log_content += e.stderr if e.stderr else "\n"
                    logger.debug(f"bug_log_content {bug_log_content}")
                    with open(bug_log_path, 'w') as bug_log_file:
                        bug_log_file.write(bug_log_content)

                    try:
                        print("Start exploring potential bugs and creating fixing plan")
                        tree = await self.get_tree_txt_files()
                        overview = self.read_txt_files(txt_files)

                        # Ensure basename list is updated without duplicates
                        fixing_related_files.update(list(self.basename))
                        fixing_related_files.update(list(totalfile))

                        logger.debug("Start exploring potential bugs and creating fixing plan")
                        fix_plans = await self.bugExplorer.get_bugFixed_suggest_requests(list(fixing_related_files), overview)
                        logger.debug("Done exploring bugs and creating fixing plan")

                        Has_Bugs = fix_plans['Has_Bugs']

                        if Has_Bugs == "True" or Has_Bugs == True:
                            logger.debug("There are some potential bugs, let me fix it!")

                            logger.debug(f"Attempt to fix on {retries + 1} try")
                            steps = fix_plans.get('steps', [])

                            for step in steps:
                                file_name = step['file_name']
                                totalfile.add(file_name)

                            await self.self_healing.get_fixing_requests(steps)

                        else:
                            logger.debug("You are good to go! There are no potential bugs!")
                            return []
                    except requests.exceptions.HTTPError as http_error:
                        if http_error.response.status_code == 429:
                            wait_time = 2 ** retries
                            logger.info(f"Rate limit exceeded, retrying in {wait_time} seconds...")
                            time.sleep(wait_time)  # Exponential backoff
                        else:
                            raise

                    retries += 1
                    continue
            if not error_flag:
                logger.info(
                    f"Build succeeded after {retries + 1} tries" if retries > 0 else "Build succeeded on the first try")
                return list(totalfile)

        # Ensure the bug log file is removed if the build succeeds
        if os.path.exists(bug_log_path):
            os.remove(bug_log_path)
        self.self_healing.clear_conversation_history()
        self.bugExplorer.clear_conversation_history()
        print("Build failed after maximum retries")
        return []


class JavaCompiler(Compiler):
    def compile_and_run(self):
        print(f"Compiling and executing Java file: {self.file_path}")
        compile_result = subprocess.run(['javac', self.file_path], capture_output=True, text=True)
        if compile_result.returncode != 0:
            print(f"Compilation failed: {compile_result.stderr}")
            return

        # Extract the class name from the file path
        class_name = self.file_path.split('/')[-1].replace('.java', '')

        # Run the compiled Java class
        run_result = subprocess.run(['java', class_name], capture_output=True, text=True)
        print(run_result.stdout)
        if run_result.stderr:
            print(run_result.stderr)


class GoCompiler(Compiler):
    def compile_and_run(self):
        print(f"Compiling and executing Go file: {self.file_path}")
        result = subprocess.run(['go', 'run', self.file_path], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)


# ======================================================
class CompilerFactory(ABC):
    @abstractmethod
    def create_compiler(self, compiler_type: CompilerType, file_path: str) -> Compiler:
        pass


class ConcreteCompilerFactory(CompilerFactory):
    def create_compiler(self, compiler_type, basename, role, directory_path, api_key, endpoint, deployment_id,
                        max_tokens, scheme, commands) -> Compiler:
        if compiler_type == CompilerType.PYTHON.value:
            return PythonCompiler(basename, role, directory_path, api_key, endpoint, deployment_id, max_tokens, scheme,
                                  commands)
        elif compiler_type == CompilerType.JAVA.value:
            return JavaCompiler(directory_path, basename, role)
        elif compiler_type == CompilerType.GO.value:
            return GoCompiler(directory_path, basename, role)
        else:
            raise ValueError(f"Unknown compiler type: {compiler_type}")


# Example usage
if __name__ == "__main__":
    factory = ConcreteCompilerFactory()

    # Example file paths
    python_file_path = 'example.py'
    java_file_path = 'Example.java'
    go_file_path = 'example.go'

    # Create and execute the Python compiler
    python_compiler = factory.create_compiler(CompilerType.PYTHON, python_file_path)
    python_compiler.compile_and_run()

    # Create and execute the Java compiler
    java_compiler = factory.create_compiler(CompilerType.JAVA, java_file_path)
    java_compiler.compile_and_run()

    # Create and execute the Go compiler
    go_compiler = factory.create_compiler(CompilerType.GO, go_file_path)
    go_compiler.compile_and_run()
