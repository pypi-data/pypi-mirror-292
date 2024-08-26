import os
import aiohttp
import asyncio
import json
import sys

from util.portkey import AIGateway

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.utils import clean_json
from json_repair import repair_json
from log.logger_config import get_logger
logger = get_logger(__name__)


class FirstPromptAgent:
    def __init__(self, max_tokens):
        self.max_tokens = max_tokens
        self.ai = AIGateway()

    async def get_prePrompt_plans(self, user_prompt):
        """
        Get development plans for a list of txt files from Azure OpenAI based on the user prompt.

        Args:
            files (list): List of file paths.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a senior iOS developer and prompt engineering specialist. Analyze the provided project files and the user's prompt and response in JSON format. Follow these guidelines:\n\n"
                        "pipeline: You need to pick one best pipeline that fits the user's prompt. Only respond with a number for the specific pipeline you pick, such as 1, 2, 3 or 4, following the guideline below:\n"
                        "1. Explainable: Must use if user make a normal prompt, or request explain, QA about the current project.\n"
                        "2. Actionable: Must use If the user request to build app, fix bug, create code or files.\n"
                        "3. Exit: Must use only If the user request to exit, quit the program.\n"
                        "The JSON response must follow this format:\n\n"
                        "{\n"
                        '    "pipeline": "1 or 2 or 3"\n'
                        "}\n\n"
                        "Return only a valid JSON response without additional text or Markdown symbols or invalid escapes."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"User original prompt:\n{user_prompt}\n\n"
                    )
                }
            ]
            response = await self.ai.prompt(messages, self.max_tokens, 0.2, 0.1)
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            good_json_string = repair_json(response.choices[0].message.content)
            plan_json = json.loads(good_json_string)
            return plan_json
        except Exception as e:
            return {
                "reason": e
            }
