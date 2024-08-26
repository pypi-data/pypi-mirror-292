import os
import aiohttp
import asyncio
import json
import sys
from fsd.log.logger_config import get_logger
from fsd.util.portkey import AIGateway
logger = get_logger(__name__)

class LightCodeAgent:
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

    def is_asset_file(self, file_name):
        asset_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',  # Image files
            '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv',    # Video files
            '.mp3', '.wav', '.aac', '.ogg', '.flac',            # Audio files
            '.svg', '.ico',                                     # Other common asset files
            '.webp', '.heic', '.m4v', '.mpg', '.mpeg'           # Additional formats
        }
        return any(file_name.lower().endswith(ext) for ext in asset_extensions)

    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def initial_setup(self, role):
        """
        Initialize the conversation with a prompt for the assistant.

        Args:
            user_prompt (str): The user's prompt to initiate the conversation.
        """
        prompt = (
            f"You are a senior {role} and coder agent.\n"
            "\n"
            "# Exclusions\n"
            "Capabilities that you don’t have right now, ignore these related tasks:\n"
            "- Third party integration/installation\n"
            "- Create Core data\n"
            "- Install Networking dependencies like Firebase, AWS\n"
            "- Create new Test file tasks\n"
            "- Can't add new images, using existing local images\n"
            "- Can't add new sounds, using existing local sounds\n"
            "\n"
            "Respond with only the updated code for the file.\n"
            "Do not remove the file's default information at the top.\n"
            "Respond with only purely valid code without additional text or Markdown symbols."
        )

        self.conversation_history.append({"role": "system", "content": prompt})


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

    async def get_working(self, session, file, prompt, all_file_contents, tech_stack):
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
            user_prompt = (
                f"User request: {prompt}\n\n - "
                f"Related support context: {all_file_contents}\n\n - "
                f"Now work on this file. Respond with only valid code without additional description or any Markdown symbols: {file_content}\n"
                f"Please strictly follow the exact syntax and formatting for {tech_stack}. "
                f"Always keep the file default description for {tech_stack}."
            )

            self.conversation_history.append({"role": "user", "content": user_prompt})

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
            logger.info(f"All code written successfully in {file_path}.")
        except Exception as e:
            logger.info(f"Error writting code. Error: {e}")

    async def get_workings(self, files, role):
        """
        Format the content of all provided files using Azure OpenAI API.

        Args:
            files (list): List of file paths to be formatted.
            role (str): The user's role to initiate the formatting request.
        """

        # Step to remove all empty files from the list
        files = [file for file in files if file]

        processed_files = []
        self.initial_setup(role)
        async with aiohttp.ClientSession() as session:
            for item in files:
                file = item['file_name']

                # Skip asset files
                if self.is_asset_file(file):
                    logger.info(f"Skipping asset file: {file}")
                    continue

                context_files = item['context_files']
                prompt = item['prompt']
                tech_stack = item['tech_stack']
                all_file_contents = ""

                context_files_to_process = self.scan_needed_files(context_files)

                for file_path in context_files_to_process:
                    file_content = self.read_file_content(file_path)
                    if file_content:
                        all_file_contents += f"\n\nFile: {file_path}\n{file_content}"

                file_path = self.scan_for_single_file(file)
                processed_files.append(file)
                code = await self.get_working(session, file_path, prompt, all_file_contents, tech_stack)
                if code:
                    await self.replace_all_code_in_file(file_path, code)
                    logger.info(f"Code completed for: {file}")

        return processed_files
