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

class GeneralExplainerAgent:
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

    async def get_normal_answer_plan(self, session, user_prompt, language):
        """
        Get a development plan for all txt files from Azure OpenAI based on the user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            user_prompt (str): The user's prompt.
            language (str): The language in which the response should be given.

        Returns:
            dict: The development plan or error reason.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "Your name is Zinley, an on-device software engineer.\n\n"
                    "You need to reply to the user prompt and respond in the provided request language.\n\n"
                )
            },
            {
                "role": "user",
                "content": (
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


    async def get_normal_answer_plans(self, user_prompt, language):
        """
        Get development plans for a list of txt files from Azure OpenAI based on the user prompt.

        Args:
            files (list): List of file paths.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """

        async with aiohttp.ClientSession() as session:
            plan = await self.get_normal_answer_plan(session, user_prompt, language)
            return plan
