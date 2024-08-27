import os
import aiohttp
import asyncio
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fsd.util.utils import clean_json
from fsd.util.portkey import AIGateway
from json_repair import repair_json
from fsd.log.logger_config import get_logger
logger = get_logger(__name__)
class ExplainablePrePromptAgent:
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

        for root, dirs, files in os.walk(self.directory_path):
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

    async def get_prePrompt_plan(self, session, user_prompt):
        """
        Get a development plan for all txt files from Azure OpenAI based on the user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a prompt engineering specialist. Analyze the provided project files and the user's prompt and respond in JSON format. Follow these guidelines:\n\n"
                    "original_prompt_language: Determine the user's main prompt language, such as English, Vietnamese, Indian, etc.\n"
                    "processed_prompt: If the user's original prompt is not in English, translate it to 100% English. Correct grammar, ensure it is clear, concise, and based on current project insights. Keep it crisp and short, avoiding confusion.\n"
                    "pipeline: You need to pick one best pipeline that fits the user's prompt. Only respond with a number for the specific pipeline you pick, such as 1, 2, following the guideline below:\n"
                    "1. Need context: Use if the user asks about the project, context insights to answer.\n"
                    "2. Don't need context: Use if the user asks about general things and can answer without context insights.\n"
                    "The JSON response must follow this format:\n\n"
                    "{\n"
                    '    "processed_prompt": "",\n'
                    '    "original_prompt_language": "Vietnamese, English, Chinese, etc.",\n'
                    '    "pipeline": "1 or 2"\n'
                    "}\n\n"
                    "Return only a valid JSON response without additional text or Markdown symbols or invalid escapes."
                )
            },
            {
                "role": "user",
                "content": f"User original prompt:\n{user_prompt}\n\n"
            }
        ]

        try:
            response = await self.ai.prompt(messages, self.max_tokens, 0.2, 0.1)
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            good_json_string = repair_json(response.choices[0].message.content)
            plan_json = json.loads(good_json_string)
            return plan_json
        except Exception as e:
            return {
                "reason": str(e)
            }

    async def get_prePrompt_plans(self, user_prompt):
        """
        Get development plans for a list of txt files from Azure OpenAI based on the user prompt.

        Args:
            files (list): List of file paths.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """

        async with aiohttp.ClientSession() as session:
            plan = await self.get_prePrompt_plan(session, user_prompt)
            return plan
