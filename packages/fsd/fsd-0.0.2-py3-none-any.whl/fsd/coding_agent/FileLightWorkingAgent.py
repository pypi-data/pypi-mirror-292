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

class FileLightWorkingAgent:
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

    def read_file_content(self, file_path):
        """
        Read and return the content of the specified file.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: Content of the file, or None if an error occurred.
        """
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            logger.info(f"Failed to read file {file_path}: {e}")
            return None

    async def get_file_planning(self, session, idea, tree, role):
        """
        Request file planning from Azure OpenAI API for a given idea and project structure.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            idea (str): The general plan idea.
            tree (str): The project structure.
            role (str): The role or identity of the assistant in this scenario.

        Returns:
            dict: JSON response with the plan or an error reason.
        """
        prompt = (
            f"You are a {role}. From the provided request, build a JSON to list all working_files to be implemented. Provide only a JSON response without any additional text or Markdown formatting. "
            "file_name must include only the file names that the user mentions to work on, not the whole path. "
            "prompt must include precisely what to be done as a prompt in this specific file. "
            "context_files: Identify and provide a list of relevant existing context files necessary for understanding and completing this work if applicable.\n"
            "context_files: Must exclude all files related to assets, development environments, configurations, or functional files like those used by IDEs.\n"
            "context_files: Must not overlap with file_name.\n"
            "context_files: If there are no relevant context files, mention that briefly.\n"
            "Use this JSON format:\n"
            "{\n"
            "    \"working_files\": [\n"
            "        {\n"
            "            \"context_files\": [\"file1.extension\", \"file2.extension\", \"file3.extension\"],\n"
            "            \"file_name\": \"LoginViewController.extension\",\n"
            "            \"tech_stack\": \"Programming language used for this file\",\n"
            "            \"prompt\": \"Detailed descriptions and explanations, step by step, on how to fix each problem and each bug. (Need to list the exact scope of the damaged code and how to fix it)\"\n"
            "        }\n"
            "    ]\n"
            "}\n"
            "Return only valid JSON without Markdown symbols or invalid escapes."
        )

        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": f"This is the user's request:\n{idea}\nThis is the current project overview:\n{tree}\n"
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


    async def get_file_plannings(self, idea, tree, role):
        """
        Request file planning from Azure OpenAI API for a given idea and project structure.

        Args:
            idea (str): The general plan idea.
            tree (list): List of file paths representing the project structure.

        Returns:
            dict: JSON response with the plan.
        """
        async with aiohttp.ClientSession() as session:
            all_file_contents = ""

            for file_path in tree:
                file_content = self.read_file_content(file_path)
                if file_content:
                    all_file_contents += f"\n\nFile: {file_path}\n{file_content}"

            plan = await self.get_file_planning(session, idea, all_file_contents, role)
            return plan
