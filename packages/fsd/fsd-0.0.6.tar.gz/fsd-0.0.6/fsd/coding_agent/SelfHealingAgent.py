import os
import sys
import asyncio
import re
import aiohttp
import json
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fsd.util.utils import get_current_time_formatted, clean_json
from fsd.util.portkey import AIGateway
from json_repair import repair_json
from fsd.log.logger_config import get_logger
logger = get_logger(__name__)

class SelfHealingAgent:

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

    def get_current_time_formatted(self):
        """Get the current time formatted as mm/dd/yy."""
        current_time = datetime.now()
        formatted_time = current_time.strftime("%m/%d/%y")
        return formatted_time

    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def initial_setup(self, role):
        """
        Initialize the conversation with a system prompt and user context.
        """
        prompt = (
            f"You are a senior software engineer working as a fixing bug agent. You will receive detailed fixing bug instructions, current damaged file context and all current related files. Your need to work on a specific file to resolve bugs. "
            "Resolve problem without changing / impacting original features and functional.\n"
            "Respond with new entirely full code for the current fixing file based on the provided fixing instructions.\n"
            "Never change or re-format file original default description, keep it the same as original.\n"
            "Respond with only a valid code response without additional text, Markdown symbols."
        )

        self.conversation_history.append({"role": "system", "content": prompt})

    def scan_for_single_file(self, filename):
        """
        Scan for a single specified file in the specified directory.

        Args:
            filename (str): The name of the file to look for.

        Returns:
            str: Path to the specified file if found, else None.
        """
        if not os.path.exists(self.directory_path):
            logger.info(f"Directory does not exist: {self.directory_path}")
            return None

        for root, _, files in os.walk(self.directory_path):
            if filename in files:
                return os.path.join(root, filename)

        return None

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
            logger.info(f"Directory does not exist: {self.directory_path}")
            return found_files

        for root, _, files in os.walk(self.directory_path):
            for filename in filenames:
                if filename in files:
                    file_path = os.path.join(root, filename)
                    found_files.append(file_path)
        return found_files

    def read_file_content(self, file_path):
        """
        Read the content of a specified file.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: Content of the file, or None if an error occurs.
        """
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            logger.info(f"Failed to read file {file_path}: {e}")
            return None

    def read_all_file_content(self, all_path):
        """
        Read the content of all specified files.

        Args:
            all_path (list): List of file paths.

        Returns:
            str: Concatenated content of all files.
        """
        all_context = ""

        for path in all_path:
            file_context = self.read_file_content(path)
            all_context += f"\n\nFile: {path}\n{file_context}"

        return all_context

    async def get_fixing_request(self, session, instruction, file_content, all_file_content, tech_stack):
        """
        Get fixing response for the given instruction and context from Azure OpenAI.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            instruction (str): The fixing instructions.
            file_content (str): The content of the file to be fixed.
            all_file_content (str): The content of all related files.

        Returns:
            dict: Fixing response or error reason.
        """

        prompt = ""

        if all_file_content != "":
            prompt = (
                f"Current damaged file:\n{file_content}\n\n"
                f"Related files context:\n{all_file_content}\n\n"
                f"Follow this instructions:\n{instruction}\n\n"
                f"Please strictly follow the exact syntax and formatting for {tech_stack}\n\n"
                f"Always keep the file default description for {tech_stack}.\n"
                "Must respond with only valid new code without additional any Markdown symbols.\n"
            )
        else:
            prompt = (
                f"Current damaged file:\n{file_content}\n\n"
                f"Follow this instructions:\n{instruction}\n\n"
                f"Please strictly follow the exact syntax and formatting for {tech_stack}\n\n"
                f"Always keep the file default description for {tech_stack}.\n"
                "Must respond with only valid new code without additional any Markdown symbols.\n"
            )

        self.conversation_history.append({"role": "user", "content": prompt})

        try:
            response = await self.ai.prompt(self.conversation_history, self.max_tokens, 0.2, 0.1)
            self.conversation_history.pop()
            return response.choices[0].message.content
        except Exception as e:
            logger.info(f"Failed: {e}")
            return {
                "reason": str(e)
            }

    async def get_fixing_requests(self, instructions):
        """
        Get fixing responses for a list of instructions from Azure OpenAI based on user prompt.

        Args:
            instructions (list): List of instructions for fixing bugs.

        Returns:
            dict: Fixing response or error reason.
        """
        for instruction in instructions:
            file_name = instruction['file_name']
            tech_stack = instruction['tech_stack']
            list_related_file_name = instruction['list_related_file_name']
            all_comprehensive_solutions_for_each_bugs = instruction['all_comprehensive_solutions_for_each_bug']
            if file_name in list_related_file_name:
                list_related_file_name.remove(file_name)

            if len(list_related_file_name) == 0:
                main_path = self.scan_for_single_file(file_name)
                file_content = self.read_file_content(main_path)
                logger.info(f"Working on: {instruction['Solution_detail_title']}")
                async with aiohttp.ClientSession() as session:
                    code = await self.get_fixing_request(session, all_comprehensive_solutions_for_each_bugs, file_content, "", tech_stack)
                    await self.replace_all_code_in_file(main_path, code)
                    logger.info(f"Done tasks for: {instruction['Solution_detail_title']}")
            else:
                main_path = self.scan_for_single_file(file_name)
                all_path = self.scan_needed_files(list_related_file_name)
                file_content = self.read_file_content(main_path)
                all_file_content = self.read_all_file_content(all_path)
                logger.info(f"Working on: {instruction['Solution_detail_title']}")
                async with aiohttp.ClientSession() as session:
                    code = await self.get_fixing_request(session, all_comprehensive_solutions_for_each_bugs, file_content, all_file_content, tech_stack)
                    await self.replace_all_code_in_file(main_path, code)
                    logger.info(f"Done tasks for: {instruction['Solution_detail_title']}")

    async def replace_all_code_in_file(self, file_path, new_code_snippet):
        """
        Replace the entire content of a file with the new code snippet.

        Args:
            file_path (str): Path to the file.
            new_code_snippet (str): New code to replace the current content.
        """
        try:
            with open(file_path, 'w') as file:
                file.write(new_code_snippet)
            logger.info(f"The codes have been fixed successfully written in... {file_path}.")
        except Exception as e:
            logger.info(f"Error fixing code. Error: {e}")
