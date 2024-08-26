import os
import sys
import asyncio
from datetime import datetime
import aiohttp
import json
import re
from json_repair import repair_json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fsd.util.utils import get_current_time_formatted, clean_json
from fsd.util.portkey import AIGateway
from fsd.log.logger_config import get_logger
logger = get_logger(__name__)

class CodingAgent:
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
        """Return the current time formatted as mm/dd/yy."""
        current_time = datetime.now()
        formatted_time = current_time.strftime("%m/%d/%y")
        return formatted_time

    def initial_setup(self, context_files, instructions, context, role):
        """Initialize the setup with the provided instructions and context."""

        scope_explanation = (
            "code: Return the full new code for this specific file.\n"
            "Title: What are you working on this file?\n"
            f"If this is a new file, update {self.get_current_time_formatted()} on the file description.\n"
        )

        prompt = (
            f"You are a senior {role} working as a coding agent. You will receive detailed instructions to work on. "
            "Respond with exact JSON format specifying what to work on each specific file based on the provided instructions.\n\n"
            "Your response must follow exact as this JSON structure.\n"
            "{\n"
            "    \"Title\": \"\",\n"
            "    \"code\": \"func addNumbers(a: Int, b: Int) -> Int {\\n    return a + b\\n}\"\n"
            "}\n"
            f"Explanation and rules: {scope_explanation}"
            "Never change or re-format file original default description, keep it the same as original.\n"
            "For code: Respond with only valid pure code without any Markdown symbols.\n"
            "For code: If the old cold has any Markdown symbols, please remove it.\n"
            "For code: Your code must be as enterprise level, comprehensive features from original requirements..\n"
            "Your code must always be:\n"
            "- Clean and comprehensive, demonstrating senior-level expertise.\n"
            "- Include detailed comments or notices for each function, class, and snippet.\n"
            "- Adhere to safety and error-catching practices to prevent crashes.\n"
            "- Ensure UI rendering is not done on the main thread.\n"
            "- Avoid all performance issue related to UI and memory leaking.\n"
            "Return only a valid JSON response without additional text, Markdown symbols, or invalid escapes."
        )

        self.conversation_history.append({"role": "system", "content": prompt})
        self.conversation_history.append({"role": "user", "content": f"These are your instructions: {instructions} and the current context: {context}"})
        self.conversation_history.append({"role": "assistant", "content": "Got it! I will follow exactly to achieve this."})

        if context_files:
            all_file_contents = ""

            files = self.scan_needed_files(context_files)

            for file_path in files:
                file_content = self.read_file_content(file_path)
                if file_content:
                    all_file_contents += f"\n\nFile: {file_path}\n{file_content}"


            self.conversation_history.append({"role": "user", "content": f"These are all the supported files to provide enough context: {all_file_contents}"})
            self.conversation_history.append({"role": "assistant", "content": "Got it! I have carefully read the provided context to perform the task."})


    def scan_for_single_file(self, filename):
        """
        Scan for a single specified file in the specified directory.

        Args:
            filename (str): The name of the file to look for.

        Returns:
            str: Path to the specified file if found, else None.
        """
        if not os.path.exists(self.directory_path):
            logger.debug(f"Directory does not exist: {self.directory_path}")
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
            logger.debug(f"Directory does not exist: {self.directory_path}")
            return found_files

        for root, _, files in os.walk(self.directory_path):
            for filename in filenames:
                if filename in files:
                    file_path = os.path.join(root, filename)
                    found_files.append(file_path)

        return found_files

    def read_file_content(self, file_path):
        """
        Read and return the content of the specified file.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: Content of the file.
        """
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            logger.info(f"Failed to read file {file_path}: {e}")
            return None


    async def get_coding_request(self, session, is_first, title, file, techStack):
        """
        Get coding response for the given instruction and context from Azure OpenAI.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            is_first (bool): Flag to indicate if it's the first request.
            title (str): Title of the coding task.
            file (str): Name of the file to work on.
            techStack (str): The technology stack for which the code should be written.

        Returns:
            dict: The code response or error reason.
        """
        # Determine the prompt based on whether it is the first request
        if is_first:
            prompt = (
                f"Begin to work on {file}. "
                f"Return with an exact JSON response example, ensuring that the code field contains valid code without additional descriptions or any Markdown symbols. "
                f"Please strictly follow the exact syntax and formatting for {techStack}. "
                f"Always keep the file default description for {techStack}. "
                f"Provide a comprehensive senior level code solution to achieve the ultimate goal from the instruction."
            )
        else:
            prompt = (
                f"{title} is complete. "
                f"Now, work on {file} and return with an exact JSON response example, ensuring that the code field contains valid code without additional descriptions or any Markdown symbols. "
                f"Please strictly follow the exact syntax and formatting for {techStack}. "
                f"Always keep the file default description for {techStack}. "
                f"Provide a comprehensive senior level code solution to achieve the ultimate goal from the instruction."
            )

        self.conversation_history.append({"role": "user", "content": prompt})

        try:
            response = await self.ai.prompt(self.conversation_history, self.max_tokens, 0.2, 0.1)
            self.conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
            res = json.loads(response.choices[0].message.content)
            return res
        except json.JSONDecodeError:
            good_json_string = repair_json(response.choices[0].message.content)
            plan_json = json.loads(good_json_string)
            return plan_json
        except Exception as e:
            logger.info(f"Failed: {e}")
            return {
                "reason": str(e)
            }


    async def get_coding_requests(self, is_first, title, file, techStack):
        """
        Get coding responses for a list of files from Azure OpenAI based on user instruction.

        Args:
            is_first (bool): Flag to indicate if it's the first request.
            title (str): Title of the coding task.

        Returns:
            dict: The code response or error reason.
        """
        async with aiohttp.ClientSession() as session:
            return await self.get_coding_request(session, is_first, title, file, techStack)

    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
