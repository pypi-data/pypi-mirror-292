import os
import aiohttp
import asyncio
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import clean_json
from util.portkey import AIGateway
from json_repair import repair_json
from log.logger_config import get_logger
logger = get_logger(__name__)

class MainExplainerAgent:
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
        self.ai = AIGateway()

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

        for root, dirs, files in os.walk(self.directory_path):
            for filename in filenames:
                if filename in files:
                    file_path = os.path.join(root, filename)
                    found_files.append(file_path)
        return found_files

    def read_file_content(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            logger.info(f"Failed to read file {file_path}: {e}")
            return None

    def read_all_file_content(self, all_path):
        all_context = ""

        for path in all_path:
            file_context = self.read_file_content(path)
            all_context += f"\n\nFile: {path}\n{file_context}"

        return all_context

    async def get_answer_plan(self, session, user_prompt, language, all_file_content):
        """
        Get a development plan for all txt files from Azure OpenAI based on the user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            user_prompt (str): The user's prompt.
            language (str): The language in which the response should be given.
            all_file_content (str): The concatenated contents of all files.

        Returns:
            dict: The development plan or error reason.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "Your name is Zinley, an on-device software engineer.\n\n"
                    "Use the provided context to answer the user's prompt.\n\n"
                    "You need to reply in the provided request language.\n\n"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{all_file_content}\n\n"
                    f"User prompt:\n{user_prompt}\n\n"
                    f"You must respond in this language:\n{language}\n\n"
                )
            }
        ]

        try:
            response = await self.ai.prompt(messages, self.max_tokens, 0.2, 0.1)
            return response.choices[0].message.content
        except Exception as e:
            return {
                "reason": str(e)
            }


    async def get_answer_plans(self, user_prompt, language, files):
        """
        Get development plans for a list of txt files from Azure OpenAI based on the user prompt.

        Args:
            files (list): List of file paths.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """
        # Step to remove all empty files from the list
        files = [file for file in files if file]

        all_path = self.scan_needed_files(files)
        all_file_content = self.read_all_file_content(all_path)

        async with aiohttp.ClientSession() as session:
            plan = await self.get_answer_plan(session, user_prompt, language, all_file_content)
            return plan
