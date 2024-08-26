import os
import aiohttp
import asyncio
import json
import sys
from json_repair import repair_json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import clean_json
from util.portkey import AIGateway
from log.logger_config import get_logger
logger = get_logger(__name__)

class TechStackAgent:
    def __init__(self, directory_path, api_key, endpoint, deployment_id, max_tokens):
        """
        Initialize the FileReplacingAgent with directory path, API key, endpoint, deployment ID, and max tokens for API requests.

        Args:
            directory_path (str): Path to the directory containing .txt files.
            api_key (str): API key for Azure OpenAI API.
            endpoint (str): Endpoint URL for Azure OpenAI.
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
        self.ai = AIGateway()

    async def get_file_planning(self, session, files):
        """
        Request file planning from Azure OpenAI API for a given list of files to determine their programming language or tech stack.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            files (list of str): List of file names to analyze.

        Returns:
            dict: JSON response with the file names and their associated programming languages or tech stacks, or an error reason.
        """
        prompt = (
            "Given a list of file names, determine the programming language or tech stack associated with each file. "
            "Return the results in JSON format with the file name as the key and the language or tech stack as the value. "
            "Ensure that the working_files include only the file names provided, without the full path. "
            "Use this JSON format:\n"
            "{\n"
            "    \"working_files\": {\n"
            "        \"file1.extension\": \"language1\",\n"
            "        \"file2.extension\": \"language2\",\n"
            "        \"file3.extension\": \"language3\"\n"
            "    }\n"
            "}\n\n"
            "Return only valid JSON without Markdown symbols or invalid escapes."
        )

        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": f"List of files:\n{files}\n"
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
            logger.info(f"Failed: {e}")
            return {
                "reason": str(e)
            }

    async def get_file_plannings(self, files):
        """
        Request file planning from Azure OpenAI API for a given idea and project structure.

        Args:
            idea (str): The general plan idea.
            tree (list): List of file paths representing the project structure.

        Returns:
            dict: JSON response with the plan.
        """
        async with aiohttp.ClientSession() as session:
            plan = await self.get_file_planning(session, files)
            return plan
