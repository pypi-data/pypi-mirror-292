import os
import aiohttp
import asyncio
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fsd.util.utils import clean_json
from fsd.util.portkey import AIGateway
from fsd.log.logger_config import get_logger
logger = get_logger(__name__)

class IdeaDevelopment:
    def __init__(self, project_path, directory_path, api_key, endpoint, deployment_id, max_tokens):
        """
        Initialize the IdeaDevelopment agent with directory path, API key, endpoint, deployment ID, and max tokens for API requests.

        Args:
            directory_path (str): Path to the directory containing .txt files.
            api_key (str): API key for Azure OpenAI API.
            endpoint (str): Endpoint URL for Azure OpenAI.
            deployment_id (str): Deployment ID for the model.
            max_tokens (int): Maximum tokens for the Azure OpenAI API response.
        """
        self.project_path = project_path
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

    def initial_setup(self, files, role):
        """
        Initialize the conversation with a system prompt and user context.
        """

        all_file_contents = ""

        for file_path in files:
            file_content = self.read_file_content(file_path)
            if file_content:
                all_file_contents += f"\n\nFile: {file_path}:\n{file_content}"


        system_prompt = (
            f"You are a senior {role}. Your task is to thoroughly analyze the provided project files and develop a comprehensive development plan. Follow these guidelines:\n\n"

            "**Guidelines:**\n"
            "- **Enterprise-Level Focus:** Ensure the plan meets enterprise standards for scalability, performance, and security.\n"
            "- **No Code in Plan:** Focus on technical and architectural planning; do not include source code.\n"
            "- **File Integrity:** Modify content within existing files without renaming them. Create new files if necessary. Clearly describe how each file will be updated or integrated.\n"
            "- **Image Handling:** Specify placeholder names for local images, ensuring automatic display with exact naming conventions.\n"
            "- **README Documentation:** Mention that a comprehensive README should be included or updated, but do not provide the README details in this plan. Focus solely on technical implementation and structural planning.\n"
            "- **File Structure and Naming:** Propose a clear, logical file and folder structure to support long-term use and expansion. Use meaningful names to avoid conflicts. Describe the desired directory structure and navigation path.\n\n"

            "**2. Detailed Implementation Plan:**\n"

            "**2.0 Ultimate Goal:**\n"
            "- Clearly state the ultimate goal of the project. Explain what the final product should achieve, who the end users are, and how this project will meet their needs. Provide a concise summary of the main objectives and deliverables.\n\n"

            "**2.1 Existing Files:**\n"
            "- Detail what needs to be implemented in these files.\n"
            "- Identify any dependencies or relationships with other files that may impact or be impacted by these changes. Describe how these relationships affect the overall system.\n"
            "- Detail the usage of any image, video, or audio assets in these files, specifying where they are included, what they represent, and why they are necessary for functionality or user experience. Include exact filenames and placement details.\n\n"

            "**2.2 New Files:**\n"
            "- Detail what needs to be implemented in these new files.\n"
            "- Describe how each new file will integrate with existing files and systems, ensuring smooth interoperability. Detail any data flow, API calls, or interactions that are necessary, and specify how this integration will be achieved.\n"
            "- Detail the usage of any image, video, or audio assets in these files, specifying where they are included, what they represent, and why they are necessary for functionality or user experience. Include exact filenames and placement details.\n\n"

            "**2.3 Dependencies (If needed for this task only):**\n"
            "- Provide a list of dependencies required for the current task only, indicating which are already installed and which need installation. Include their roles and relevance to the project.\n"
            "- Specify the exact version of each dependency to ensure stability and compatibility with the existing system. Explain why specific versions are required.\n"
            "- Include considerations for dependency updates or replacements that might improve security or performance. Justify any recommendations for changes.\n\n"

            "**2.4 Existing Context Files (if applicable):**\n"
            "- Provide a list of relevant existing context files necessary for understanding and completing the task, such as configuration files, environment settings, or other critical resources. Explain their importance and how they will be used.\n"
            "- Exclude non-essential files like assets, development environment configurations, and IDE-specific files. Clarify why these files are not included.\n"
            "- Ensure there is no overlap with Existing Files (2.1) and New Files (2.2). Clearly differentiate their roles and usage. Provide explanations to avoid confusion.\n"
            "- If no relevant context files are found, mention this briefly, confirming that all necessary files have been accounted for. Clearly state that all essential files are included and identified.\n\n"
        )




        self.conversation_history.append({"role": "system", "content": system_prompt})
        self.conversation_history.append({"role": "user", "content":  f"Here are the current project files:\n{all_file_contents}\n"})
        self.conversation_history.append({"role": "assistant", "content": "Got it! Give me user prompt so i can support them."})


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

    async def get_idea_plan(self, session, user_prompt):
        """
        Get development plan for all txt files from Azure OpenAI based on user prompt.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """
        prompt = (
             f"Follow the user prompt strictly and provide a no code response:\n{user_prompt}\n\n"
        )

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

    async def get_feedback_plan(self, session, user_prompt):
        """
        Get feedback plan for modifying the development plan based on user feedback.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            user_prompt (str): The user's feedback prompt.

        Returns:
            dict: Modified development plan or error reason.
        """
        prompt = (
             f"Follow the user feedback strictly to modify and provide a no code response:\n{user_prompt}\n\n"
        )

        self.conversation_history.append({"role": "user", "content": prompt})

        try:
            response = await self.ai.prompt(self.conversation_history, self.max_tokens, 0.2, 0.1)
            self.conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
            return response.choices[0].message.content
        except Exception as e:
            return {
                "reason": str(e)
            }

    async def get_idea_plans(self, user_prompt):
        """
        Get development plans for a list of txt files from Azure OpenAI based on user prompt.

        Args:
            files (list): List of file paths.
            user_prompt (str): The user's prompt.

        Returns:
            dict: Development plan or error reason.
        """

        async with aiohttp.ClientSession() as session:
            plan = await self.get_idea_plan(session, user_prompt)
            return plan

    async def get_feedback_plans(self, user_prompt):
        """
        Get feedback plans for modifying the development plan based on user feedback.

        Args:
            user_prompt (str): The user's feedback prompt.

        Returns:
            dict: Modified development plan or error reason.
        """
        async with aiohttp.ClientSession() as session:
            plan = await self.get_feedback_plan(session, user_prompt)
            return plan
