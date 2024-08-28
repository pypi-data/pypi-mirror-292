import os
import sys
import json
from json_repair import repair_json
from fsd.util.portkey import AIGateway
from fsd.log.logger_config import get_logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fsd.util.utils import clean_json

logger = get_logger(__name__)

class FirstPromptAgent:
    def __init__(self, max_tokens):
        self.max_tokens = max_tokens
        self.ai = AIGateway()

    async def get_prePrompt_plans(self, user_prompt):
        """
        Get development plans based on the user prompt.

        Args:
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """
        try:
            messages = self._create_messages(user_prompt)
            response = await self.ai.prompt(messages, self.max_tokens, 0.2, 0.1)
            return self._parse_response(response)
        except Exception as e:
            return {"reason": str(e)}

    def _create_messages(self, user_prompt):
        system_content = (
            "You are a senior iOS developer and prompt engineering specialist. "
            "Analyze the user's prompt and respond in JSON format. Follow these guidelines:\n\n"
            "pipeline: Pick one best pipeline that fits the user's prompt. "
            "Respond with a number (1, 2, or 3) for the specific pipeline:\n"
            "1. Explainable: Use for normal prompts, explanations, or QA about the current project.\n"
            "2. Actionable: Use for requests to build apps, fix bugs, create code or files.\n"
            "3. Exit: Use only for requests to exit or quit the program.\n"
            "The JSON response must follow this format:\n"
            '{"pipeline": "1 or 2 or 3"}\n'
            "Return only a valid JSON response without additional text or symbols."
        )
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": f"User original prompt:\n{user_prompt}"}
        ]

    def _parse_response(self, response):
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            repaired_json = repair_json(response.choices[0].message.content)
            return json.loads(repaired_json)