import os
import sys
import asyncio
import re
from json_repair import repair_json
import aiohttp
import json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fsd.util.utils import get_current_time_formatted, clean_json
from fsd.util.portkey import AIGateway
from fsd.log.logger_config import get_logger
logger = get_logger(__name__)

class BugExplorer:
    def __init__(self, directory_path, api_key, endpoint, deployment_id, max_tokens):
        self.directory_path = directory_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.conversation_history = []
        self.ai = AIGateway()

    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def initial_setup(self, initial_instruction, role):
        """Set up the initial prompt for the bug-fixing agent."""
        prompt = (
            "You are a senior software engineer working as a bug-scanner agent. Your task is to analyze the provided project context to identify only genuine risk errors, focusing on the following types of errors: "
            "syntax errors, integration errors, performance issues, memory leaks, security vulnerabilities, and any other critical errors that could impact the functionality or stability of the project. "
            "Provide detailed, structured steps to fix the project, ensuring that the root cause of each bug is addressed, rather than merely fixing symptoms across multiple files. "
            "Please adhere strictly to the following rules: "
            "(1) If no potential bugs are found, set 'Has_Bugs' to False; otherwise, set it to True. \n"
            "(2) The 'file_name' should include only the name of the file that needs attention, without any path. \n"
            "(3) Each step should involve only one file. \n"
            "(4) The 'list_related_file_name' should list only the names of files that could potentially be related to or impacted by issues in the working file; if there are no such files, return an empty list. \n"
            "Scan for errors only if the code indicates a potential risk. The specific types of errors to scan for include: \n"
            "- Syntax errors: Errors in the code that prevent it from being parsed or compiled correctly. \n"
            "- Integration errors: Issues that arise when different parts of the code interact with each other. \n"
            "- Performance issues: Code that may cause slowdowns or inefficient use of resources. \n"
            "- Memory leaks: Parts of the code that may cause excessive memory usage without releasing it. \n"
            "- Security vulnerabilities: Code that may expose the project to security risks. \n"
            "- Other critical errors: Any other errors that could impact the project's functionality or stability. \n"
            "If no potential bugs are found, the JSON response should strictly follow this format:\n\n"
            "{\n"
            "    \"Has_Bugs\": False,\n"
            "    \"steps\": []\n"
            "}\n"
            "If potential bugs are found, the JSON response should strictly follow this format:\n\n"
            "{\n"
            "    \"Has_Bugs\": True,\n"
            "    \"steps\": [\n"
            "        {\n"
            "            \"Step\": 1,\n"
            "            \"file_name\": \"LoginViewController.extension\",\n"
            "            \"tech_stack\": \"Programming language or framework used for this file\",\n"
            "            \"list_related_file_name\": [\"LoginViewController.extension\", \"AnotherFile.extension\"],\n"
            "            \"Solution_detail_title\": \"Fixing a login screen for user authentication.\",\n"
            "            \"all_comprehensive_solutions_for_each_bug\": \"Provide detailed descriptions and step-by-step explanations on how to fix each identified problem and bug, specifying the exact scope of the affected code and the steps required to resolve the issue.\"\n"
            "        }\n"
            "    ]\n"
            "}\n"
            "Return only a valid JSON response without any additional text."
        )


        if initial_instruction != "":
            prompt2 = (
                "This is the original development plan. While fixing bugs, you must maintain the requirements from the original plan without modifications. \n"
                f"Here is the plan: {initial_instruction}.\n"
            )

            self.conversation_history.append({"role": "system", "content": prompt})
            self.conversation_history.append({"role": "user", "content": prompt2})
            self.conversation_history.append({"role": "assistant", "content": "Got it! I will maintain the requirements from the original development plan while fixing bugs."})
        else:
            self.conversation_history.append({"role": "system", "content": prompt})


    def scan_needed_files(self, filenames):
        """
        Scan for specified files in the specified directory.

        Args:
            filenames (list): List of filenames to look for.

        Returns:
            list: Paths to the specified files if found.
        """
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
            logger.debug(f"Failed to read file {file_path}: {e}")
            return None

    async def get_bugFixed_suggest_request(self, session, all_file_contents, overview):
        """
        Get development plan for all txt files from Azure OpenAI based on user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            all_file_contents (str): The concatenated contents of all files.
            overview (str): Project overview description.

        Returns:
            dict: Development plan or error reason.
        """

        error_prompt = (
            f"Current scanning file:\n{all_file_contents}\n\n"
            "Return only a valid JSON bug exploring response without additional text or Markdown symbols or invalid escapes.\n\n"
        ).replace("<project_directory>", self.directory_path)

        self.conversation_history.append({"role": "user", "content": error_prompt})

        try:
            response = await self.ai.prompt(self.conversation_history, self.max_tokens, 0.6, 0.7)
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            good_json_string = repair_json(response.choices[0].message.content)
            plan_json = json.loads(good_json_string)
            return plan_json
        except Exception as e:
            logger.info(f"Failed: {e}")
            return {
                "reason": e
            }

    async def get_bugFixed_suggest_requests(self, files, overview):
        """
        Get development plans for a list of txt files from Azure OpenAI based on user prompt.

        Args:
            files (list): List of file paths.
            overview (str): Overview description.

        Returns:
            dict: Development plan or error reason.
        """
        # Step to remove all empty files from the list
        filtered_lists = [os.path.basename(file) for file in files if file]

        logger.debug(f"Scanning: {filtered_lists}")

        async with aiohttp.ClientSession() as session:
            all_file_contents = ""

            # Scan needed files based on the filtered list
            final_files_paths = self.scan_needed_files(filtered_lists)

            for file_path in final_files_paths:
                try:
                    file_content = self.read_file_content(file_path)
                    if file_content:
                        all_file_contents += f"\n\nFile: {file_path}\n{file_content}"
                except Exception as e:
                    all_file_contents += f"\n\nFailed to read file {file_path}: {str(e)}"

            # Get the bug-fixed suggestion request
            plan = await self.get_bugFixed_suggest_request(session, all_file_contents, overview)
            return plan
