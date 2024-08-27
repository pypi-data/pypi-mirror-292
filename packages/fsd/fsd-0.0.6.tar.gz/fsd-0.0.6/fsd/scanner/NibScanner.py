import os
import aiohttp
import asyncio
import json

from json_repair import repair_json

class NibScanner:
    def __init__(self, project_path, api_key, endpoint, deployment_id, max_tokens):
        self.project_path = project_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def scan_files_in_project(self):
        nib_files = []
        for root, dirs, files in os.walk(self.project_path):
            if 'Pods' in root:
                continue
            for file in files:
                if file.endswith('.nib'):
                    file_path = os.path.join(root, file)
                    nib_files.append(file_path)
        return nib_files

    def read_file_content(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Failed to read file {file_path}: {e}")
            return None

    async def get_file_summary(self, session, file_path, file_content):
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are a senior iOS developer. Analyze this NIB file from an Xcode project. The file name is {os.path.basename(file_path)}. Provide only a JSON response without any additional text or Markdown formatting."
                    )
                },
                {
                    "role": "user",
                    "content": file_content
                }
            ],
            "temperature": 0.2,
            "top_p": 0.1,
            "max_tokens": self.max_tokens
        }

        url = f"{self.endpoint}/openai/deployments/{self.deployment_id}/chat/completions?api-version=2024-04-01-preview"

        async with session.post(url, headers=self.headers, json=payload) as response:
            if response.status != 200:
                response_json = await response.json()
                error_message = response_json.get('error', {}).get('message', 'Unknown error')
                return {
                    "file_path": file_path,
                    "reason": error_message
                }

            summary = await response.json()

            if 'choices' in summary and len(summary['choices']) > 0:
                message_content = summary['choices'][0]['message']['content']

                try:
                    summary_json = json.loads(message_content)
                    return {
                        "file_path": file_path,
                        "summary": summary_json
                    }
                except json.JSONDecodeError:
                    good_json_string = repair_json(message_content)
                    plan_json = json.loads(good_json_string)
                    return {
                        "file_path": file_path,
                        "summary": plan_json
                    }

    async def get_file_summaries(self, files):
        file_summaries = []
        async with aiohttp.ClientSession() as session:
            for file_path in files:
                try:
                    file_content = self.read_file_content(file_path)
                    if not file_content:
                        file_summaries.append({
                            "file_path": file_path,
                            "reason": "Failed to read file content"
                        })
                        continue

                    summary = await self.get_file_summary(session, file_path, file_content)
                    file_summaries.append(summary)
                except Exception as e:
                    file_summaries.append({
                        "file_path": file_path,
                        "reason": str(e)
                    })

        return file_summaries
