import os
import aiohttp
import asyncio
import json
import sys
from fsd.log.logger_config import get_logger
logger = get_logger(__name__)
from fsd.util.portkey import AIGateway

class FormattingAgent:
    def __init__(self, directory_path, api_key, endpoint, deployment_id, max_tokens):
        """
        Initialize the FormattingAgent with directory path, API key, endpoint, deployment ID, and max tokens for API requests.

        Args:
            directory_path (str): Path to the directory containing .txt files.
            api_key (str): API key for Azure OpenAI API.
            endpoint (str): Endpoint for the Azure OpenAI API.
            deployment_id (str): Deployment ID for the model.
            max_tokens (int): Maximum tokens for the Azure OpenAI API response.
        """
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

    def initial_setup(self, user_prompt, role):
        """
        Initialize the conversation with a prompt for the assistant.

        Args:
            user_prompt (str): The user's prompt to initiate the conversation.
        """
        prompt = (
            f"You are a senior {role} agent. Follow user request but must ensure the functionality remains the same. Respond with only the updated code for the file. Do not remove the file's default information at the top. Respond with only valid code without additional description or any Markdown symbols."
        )

        self.conversation_history.append({"role": "system", "content": prompt})
        self.conversation_history.append({"role": "user", "content": f"Cool, this is user request: {user_prompt}"})
        self.conversation_history.append({"role": "assistant", "content": "Got it! I will follow exactly and respond only with plain code without additional text or Markdown symbols."})

    def read_file_content(self, file_path):
        """
        Read the content of a given file.

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

    async def get_format(self, session, file):
        """
        Request code reformatting from Azure OpenAI API for a given file.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            file (str): Path to the file to be reformatted.

        Returns:
            str: Reformatted code or error reason.
        """
        file_content = self.read_file_content(file)
        if file_content:
            # Prepare payload for the API request
            prompt = f"Now work on this file, please follow exactly user's request. Respond with only valid code without additional description or any Markdown symbols: {file_content}"

            self.conversation_history.append({"role": "user", "content": prompt})

            try:
                response = await self.ai.prompt(self.conversation_history, self.max_tokens, 0.2, 0.1)
                self.conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
                return response.choices[0].message.content
            except Exception as e:
                logger.info(f"Failed: {e}")
                return {
                    "reason": str(e)
                }


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
            logger.info(f"All code formatted successfully in {file_path}.")
        except Exception as e:
            logger.info(f"Error formatting code. Error: {e}")

    async def get_formats(self, files, prompt, role):
        """
        Format the content of all provided files using Azure OpenAI API.

        Args:
            files (list): List of file paths to be formatted.
            prompt (str): The user's prompt to initiate the formatting request.
        """
        # Step to remove all empty files from the list
        files = [file for file in files if file]

        file_paths = self.scan_needed_files(files)
        self.initial_setup(prompt, role)
        async with aiohttp.ClientSession() as session:
            for file in file_paths:
                code = await self.get_format(session, file)
                if code:
                    await self.replace_all_code_in_file(file, code)
                    logger.info(f"Completed formatting for: {file}")
