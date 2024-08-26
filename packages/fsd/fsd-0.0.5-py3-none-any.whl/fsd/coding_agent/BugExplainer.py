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

class BugExplainer:
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
            f"You are a senior {role} working as a bug-fixing agent. Your task is to analyze the provided project context and current errors, identifying the root cause of each bug and providing detailed, structured steps to fix the project. "
            "Note that sometimes bugs may appear in multiple files but are caused by an issue in a single file. Focus on identifying and fixing the root cause rather than applying fixes to all affected files. "
            "Please adhere to the following rules: "
            "(1) Each step must involve a single file only. \n"
            "(2) The 'file_name' must include only the name of the file that needs to be worked on, without any path. \n"
            "(3) The 'list_related_file_name' must include only the names of files that could potentially be related to or impacted by the changes made in the working file; if there are no such files, return an empty list. \n"
            "(4) The 'is_new' flag should be set to 'True' if the file needs to be newly created (e.g., if it was accidentally deleted or is missing). Otherwise, set 'is_new' to 'False'. \n"
            "(5) The 'new_file_location' should specify the relative path and folder where the new file will be created, if necessary. \n"
            "The JSON response must strictly follow this format:\n\n"
            "{\n"
            "    \"steps\": [\n"
            "        {\n"
            "            \"Step\": 1,\n"
            "            \"file_name\": \"LoginViewController.extension\",\n"
            "            \"tech_stack\": \"Programming language used for this file\",\n"
            "            \"is_new\": \"True/False\",\n"
            "            \"new_file_location\": \"Relative/Path/To/Folder\",\n"
            "            \"list_related_file_name\": [\"LoginViewController.extension\", \"AnotherFile.extension\"],\n"
            "            \"Solution_detail_title\": \"Fixing a login screen for user authentication.\",\n"
            "            \"all_comprehensive_solutions_for_each_bug\": \"Detailed descriptions and explanations, step by step, on how to fix each problem and bug. (List the exact scope of the damaged code and how to fix it)\"\n"
            "        }\n"
            "    ]\n"
            "}\n"
            "Do not add any additional content beyond the example above."
            "Return only a valid JSON response without any additional text, Markdown symbols, or invalid escapes."
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
            logger.info(f"Failed to read file {file_path}: {e}")
            return None

    async def get_bugFixed_suggest_request(self, session, bug_log_path, all_file_contents, overview):
        """
        Get development plan for all txt files from Azure OpenAI based on user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            all_file_contents (str): The concatenated contents of all files.
            overview (str): Project overview description.

        Returns:
            dict: Development plan or error reason.
        """
        bug_logs = self.read_file_content(bug_log_path)
        if not bug_logs:
            return {
                "reason": "Bug log file not found or empty."
            }

        error_prompt = (
            f"Current working file:\n{all_file_contents}\n\n"
            f"Project overview:\n{overview}\n\n"
            f"Bug logs:\n{bug_logs}\n\n"
            "Return only a valid JSON format bug fix response without additional text or Markdown symbols or invalid escapes.\n\n"
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


    async def get_bugFixed_suggest_requests(self, bug_log_path, files, overview):
        """
        Get development plans for a list of txt files from Azure OpenAI based on user prompt.

        Args:
            bug_log_path (str): Path to the bug log file.
            files (list): List of file paths.
            overview (str): Overview description.

        Returns:
            dict: Development plan or error reason.
        """
        # Step to remove all empty files from the list
        filtered_lists = [file for file in files if file]

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
            plan = await self.get_bugFixed_suggest_request(session, bug_log_path, all_file_contents, overview)
            return plan
