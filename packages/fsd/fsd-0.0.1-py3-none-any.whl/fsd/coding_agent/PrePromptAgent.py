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

class PrePromptAgent:
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

    def scan_txt_files(self):
        """
        Scan for all txt files in the specified directory.

        Returns:
            list: Paths to all txt files.
        """
        txt_files = []

        if not os.path.exists(self.directory_path):
            logger.info(f"Directory does not exist: {self.directory_path}")
            return txt_files

        for root, _, files in os.walk(self.directory_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    txt_files.append(file_path)

        return txt_files

    def read_file_content(self, file_path):
        """
        Read the content of a specified file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The content of the file, or None if an error occurs.
        """
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            logger.info(f"Failed to read file {file_path}: {e}")
            return None

    async def get_prePrompt_plan(self, session, all_file_contents, user_prompt):
        """
        Get a development plan for all txt files from Azure OpenAI based on the user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            all_file_contents (str): The concatenated contents of all files.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a senior prompt engineering specialist. Analyze the provided project files and the user's prompt and respond in JSON format. Follow these guidelines:\n\n"
                    "original_prompt_language: Determine the user's main prompt language such as English, Vietnamese, Indian, etc.\n"
                    "role: Choose a specific single type of engineer role that best fits to complete the user's request for this project.\n"
                    "need_to_re_scan: If there is no file to scan, return False. Otherwise, check all the scanner files and the tree structure. If the codebase needs to be indexed again, return True; otherwise, return False.\n"
                    "processed_prompt: If the user's original prompt is not in English, translate it to English. Correct grammar, ensure it is clear, concise, and based on current project insights. Make sure it's descriptive to help coding agent build easier.\n"
                    "pipeline: You need to pick the best pipeline that fits the user's prompt. Only respond with a number for the specific pipeline you pick, such as 1, 2, 3, 4, 5, 6 following the guidelines below:\n"
                    "If the user requires a task you can perform, use the options below:\n"
                    "1. Compile error: Use only if compile errors occur.\n"
                    "2. Create/add files or folders: Use if the user only asks to add/create new files or folders.\n"
                    "3. Move files or folders: Use if the user only asks to move files or folders.\n"
                    "4. Light/Small code writer on existing code: Use for light code update requests, adding simple functions, quick updates, like changing color.\n"
                    "5. Main coding agent: Use for code builder requests, fixing non-compile error bugs (performance, fatal errors, etc.), writing a simple app/game, writing test cases. If the work requires adding new files, please use this pipeline.\n"
                    "The JSON response must follow this format:\n\n"
                    "{\n"
                    '    "processed_prompt": "",\n'
                    '    "role": "",\n'
                    '    "pipeline": "1 or 2 or 3 or 4 or 5 or 6",\n'
                    '    "original_prompt_language": "",\n'
                    '    "need_to_re_scan": "True or False"\n'
                    "}\n\n"
                    "Return only a valid JSON response without additional text or Markdown symbols."
                )
            },
            {
                "role": "user",
                "content": (
                    f"User original prompt:\n{user_prompt}\n\n"
                    f"Here are the current project files:\n{all_file_contents}\n"
                )
            }
        ]

        try:
            response = await self.ai.prompt(messages, self.max_tokens, 0.2, 0.1)
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

    async def get_prePrompt_plans(self, files, user_prompt):
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

        all_file_contents = ""

        for file_path in files:
            file_content = self.read_file_content(file_path)
            if file_content:
                all_file_contents += f"\n\nFile: {file_path}:\n{file_content}"

        async with aiohttp.ClientSession() as session:
            plan = await self.get_prePrompt_plan(session, all_file_contents, user_prompt)
            logger.info(f"Completed preparing for: {user_prompt}")
            return plan
