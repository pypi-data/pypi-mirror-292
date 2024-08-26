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

class LanguageAgent:
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

    async def get_language_plan(self, session, user_prompt, role):
        """
        Get a development plan for the given prompt from Azure OpenAI.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            user_prompt (str): The user's prompt.

        Returns:
            str: Development plan or error reason.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a senior {role} and prompt engineering specialist. "
                    "If the user's original prompt is not in English, translate it to 100% English. "
                    "Correct grammar, ensure it is clear and concise. Keep it crisp and short, avoiding confusion."
                )
            },
            {
                "role": "user",
                "content": (
                    f"User original prompt:\n{user_prompt}\n\n"
                )
            }
        ]

        try:
            response = await self.ai.prompt(messages, self.max_tokens, 0.2, 0.1)
            return response.choices[0].message.content
        except Exception as e:
            logger.info(f"Failed: {e}")
            return {
                "reason": str(e)
            }

    async def get_language_plans(self, user_prompt, role):
        """
        Get development plans based on the user prompt.

        Args:
            user_prompt (str): The user's prompt.

        Returns:
            str: Development plan or error reason.
        """
        async with aiohttp.ClientSession() as session:
            plan = await self.get_language_plan(session, user_prompt, role)
            return plan
