import json
import os
import asyncio
import re
import time
import shutil  # Import shutil for copying directories
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fsd.Scanner1.ProjectScanner1 import ProjectScanner1  # Ensure this module is correctly imported and available
from fsd.explainer.ExplainerController import ExplainerController  # Ensure this module is correctly imported and available
from fsd.coding_agent.ControllerAgent import ControllerAgent  # Ensure this module is correctly imported and available
from fsd.FirstPromptAgent import FirstPromptAgent
from fsd.util import utils
from fsd.util.portkey import AIGateway
from fsd.log.logger_config import get_logger
from fsd.util.astparser import ast_parse
logger = get_logger(__name__)
max_tokens = 4096
def run_git_command(command, cwd=None):
    """Run a Git command and return the output."""
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Git command failed: {result.stderr}")
    return result.stdout.strip()

def is_first_commit(project_path):
    try:
        if not os.path.exists(os.path.join(project_path, '.git')):
            return True
        tags = run_git_command('git tag', cwd=project_path).split('\n')
        version_numbers = [int(tag[1:]) for tag in tags if tag.startswith('v') and tag[1:].isdigit()]
        return len(version_numbers) == 0
    except Exception as e:
        logger.error(f"Failed to check if the project is a Git repository: {e}")

def init_git_versioned_project(project_path, user_prompt):
    try:
        project_name = os.path.basename(project_path)
        # Create path to analysis folder
        analysis_path = os.path.join(os.path.expanduser('~'), '.zinley/', project_name, 'Zinley')
        # Ensure the project path is a Git repository
        if not os.path.exists(os.path.join(analysis_path, '.git')):
            run_git_command('git init', cwd=analysis_path)
        # Ensure the project path is a Git repository
        if not os.path.exists(os.path.join(project_path, '.git')):
            run_git_command('git init', cwd=project_path)

        # check projec_path folder not empty then add files to git
        logger.debug(f"ls project_path = {os.listdir(project_path)}")
        if len(os.listdir(project_path)) > 1:
            run_git_command('git add .', cwd=project_path)
            run_git_command(f'git commit -m "{user_prompt}"', cwd=project_path)

        logger.info("Project initialized and version control setup.")
    except Exception as e:
        logger.error(f"Failed to initialize git versioned project: {e}")

def create_tag_version(project_path):
    try:
        project_name = os.path.basename(project_path)
        # Create path to analysis folder
        analysis_path = os.path.join(os.path.expanduser('~'), '.zinley/', project_name, 'Zinley')

         # Ensure the project path is a Git repository
        if not os.path.exists(os.path.join(project_path, '.git')):
            raise RuntimeError(f"The path {project_path} is not a Git repository.")
        # Get the list of existing tags
        tags = run_git_command('git tag', cwd=project_path).split('\n')
        logger.debug(f"tags={tags}")
        next_version = "v1"
        # if tags not empty or length > 1
        if len(tags) > 1 or tags[0] == "v1":
            version_numbers = [int(tag[1:]) for tag in tags if tag.startswith('v') and tag[1:].isdigit()]
            next_version_number = max(version_numbers, default=0) + 1
            next_version = f"v{next_version_number}"

        logger.debug(f"next_version={next_version}")
        # Create a new tag for the next version
        run_git_command(f'git tag {next_version}', cwd=project_path)

        # create tag for analysis folder
        run_git_command(f'git add .', cwd=analysis_path)
        run_git_command(f'git commit -m "{next_version}"', cwd=analysis_path)
        run_git_command(f'git tag {next_version}', cwd=analysis_path)

        logger.info(f"Project version tagged as {next_version}")
    except Exception as e:
        logger.error(f"Failed to create tag version: {e}")

def switch_tag_version(project_path, version):
    try:
        project_name = os.path.basename(project_path)
        # Create path to analysis folder
        analysis_path = os.path.join(os.path.expanduser('~'), '.zinley/', project_name, 'Zinley')

        # Ensure the project path is a Git repository
        if not os.path.exists(os.path.join(project_path, '.git')):
            raise RuntimeError(f"The path {project_path} is not a Git repository.")

        # Check out the specified version
        run_git_command(f'git checkout {version}', cwd=project_path)
        run_git_command(f'git checkout {version}', cwd=analysis_path)

        logger.info(f"Switched to version {version} and updated the project at {project_path}")

    except Exception as e:
        logger.error(f"An error occurred while switching the project version: {e}")
def create_versioned_project_copy(project_path):
    try:
        # Extract the project name from the project_path
        project_name = os.path.basename(project_path.rstrip("/"))

        # Define the base path for version control
        version_control_base_path = os.path.abspath(os.path.join(project_path, "../../Version_control"))

        # Ensure the version control base path exists
        os.makedirs(version_control_base_path, exist_ok=True)

        # Create the project folder within the version control base path if it doesn't exist
        project_version_control_path = os.path.join(version_control_base_path, project_name)
        os.makedirs(project_version_control_path, exist_ok=True)

        # Determine if v1 exists
        v1_path = os.path.join(project_version_control_path, "v1")

        # Check if v1 is empty or doesn't exist
        if not os.path.exists(v1_path) or not os.listdir(v1_path):
            # Define the destination path for the new version
            new_version_path = v1_path if not os.path.exists(v1_path) else None

            # Copy the entire project to the new version path if it is empty or doesn't exist
            if new_version_path:
                shutil.copytree(project_path, new_version_path)
                logger.info(f"Project copied to {new_version_path}")
            else:
                logger.info(f"v1 already exists and is not empty, skipping copy.")
        else:
            logger.info(f"v1 already exists and is not empty, skipping copy.")
    except Exception as e:
        logger.error(f"An error occurred while copying the project: {e}")

def copy_project_with_version_control(project_path):
    try:
        # Extract the project name from the project_path
        project_name = os.path.basename(project_path.rstrip("/"))

        # Define the base path for version control
        version_control_base_path = os.path.abspath(os.path.join(project_path, "../../Version_control"))

        # Ensure the version control base path exists
        os.makedirs(version_control_base_path, exist_ok=True)

        # Create the project folder within the version control base path if it doesn't exist
        project_version_control_path = os.path.join(version_control_base_path, project_name)
        os.makedirs(project_version_control_path, exist_ok=True)

        # Determine the next version number
        existing_versions = [d for d in os.listdir(project_version_control_path) if os.path.isdir(os.path.join(project_version_control_path, d))]
        version_numbers = [int(d[1:]) for d in existing_versions if d.startswith('v') and d[1:].isdigit()]
        next_version_number = max(version_numbers, default=0) + 1
        next_version = f"v{next_version_number}"

        # Define the destination path for the new version
        new_version_path = os.path.join(project_version_control_path, next_version)

        # Copy the entire project to the new version path
        shutil.copytree(project_path, new_version_path)

        logger.info(f"Project copied to {new_version_path}")
    except Exception as e:
        logger.error(f"An error occurred while copying the project: {e}")

def get_version_from_prompt(prompt):
    match = re.search(r'v\d+', prompt)
    if match:
        return match.group()
    else:
        raise ValueError("No version specified in the prompt")

def switch_project_version(project_path, version):
    # Extract the project name from the project_path
    project_name = os.path.basename(project_path.rstrip("/"))

    # Define the base path for version control
    version_control_base_path = os.path.abspath(os.path.join(project_path, "../../Version_control"))

    # Define the source path for the specified version
    version_path = os.path.join(version_control_base_path, project_name, version)

    # Check if the specified version exists
    if not os.path.exists(version_path):
        logger.info(f"Version {version} does not exist")
        return

    # Copy the entire version to the project path, overwriting existing files
    shutil.rmtree(project_path)
    shutil.copytree(version_path, project_path)

    logger.error(f"Switched to {version} and updated the project at {project_path}")

async def start(project_path, api_key, max_tokens, endpoint, deployment_id, schema):
    try:
        # check project_path exist
        if not os.path.exists(project_path):
            raise FileNotFoundError("Project path does not exist.")
        
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = project_path.split('/')
        project_name = parts[-1]
        
        scanner = ProjectScanner1(project_path, api_key, endpoint, deployment_id, max_tokens)
        explainer_controller = ExplainerController(os.path.join(project_path), api_key, endpoint, deployment_id, max_tokens)
        coding_controller = ControllerAgent(os.path.join(project_path), api_key, endpoint, deployment_id, max_tokens, schema)

        project_name = os.path.basename(project_path.rstrip("/"))
        analysis_path = os.path.join(os.path.expanduser('~'), ".zinley", project_name)
        result_files_exist = os.path.exists(os.path.join(analysis_path, "Zinley", "Project_analysis", "tree.txt"))
        file_modification_exist = os.path.exists(os.path.join(analysis_path, "Zinley", "Project_analysis", "file_modification_times.txt"))
        skip_scanner = ''
        if not result_files_exist or not file_modification_exist:
            logger.info("This project hasn't been scanned yet. I will scan it now!")
            skip_scanner = 'n'
        else:
            scan_files = utils.get_new_or_modified_file(project_path)
            if scan_files:
                await scanner.get_incremental_scan_started(scan_files)
                update_tree(project_path, home_directory, hidden_zinley_folder_name, project_name)
            else:
                logger.debug("No new or modified files to scan.")
                logger.info("This project has been scanned. However, please note, if you modify the code yourself, you should let us scan again to stay up to date.")
                skip_scanner = input("Do you want to skip the scanner part? (y/n): ").strip().lower()

        if skip_scanner == 'n':
            logger.info("Starting project analysis...")
            start_time = time.time()
            await scanner.get_started()
            update_tree(project_path, home_directory, hidden_zinley_folder_name, project_name)


        else:
            logger.info("Skipping scanner part...")
            output_dir = os.path.join(analysis_path, "Zinley", "Project_analysis")
            os.makedirs(output_dir, exist_ok=True)

            # Run the `tree` command and save the output to tree.txt, excluding the Zinley folder
            tree_path = os.path.join(output_dir, "tree.txt")

            # Clear the file contents before writing new content
            open(tree_path, 'w').close()

            with open(tree_path, 'w') as f:
                subprocess.run(['tree', project_path, '-I', 'Zinley'], stdout=f, text=True)

        while True:
            user_prompt_json = input("Enter your prompt (type 'exit' to quit): ")
            user_prompt, file_attachment = parse_payload(user_prompt_json, project_path)
            if file_attachment:
                scan_files = utils.get_new_or_modified_file(project_path)
                if scan_files:
                    await scanner.get_incremental_scan_started(scan_files)
                    update_tree(project_path, home_directory, hidden_zinley_folder_name, project_name)
                    
            result = await get_prePrompt(user_prompt)
            pipeline = result['pipeline']
            if pipeline == "1":
                logger.debug(f"Zinley: Sent explaining request for: {user_prompt}")
                await explainer_controller.get_started(user_prompt)
            elif pipeline == "2":
                if is_first_commit(project_path):
                    # check project_path not empty
                    if not os.listdir(project_path):
                        init_git_versioned_project(project_path, user_prompt)
                        logger.debug(f"Zinley: No files in project_path: {project_path}")
                    else:
                        init_git_versioned_project(project_path, user_prompt)
                        create_tag_version(project_path)
                # create_versioned_project_copy(project_path)
                logger.debug(f"Zinley: Sent coding request for: {user_prompt}")
                await coding_controller.get_started(user_prompt)
                logger.debug(f"Zinley: Done coding request for: {user_prompt}")
                init_git_versioned_project(project_path, user_prompt)
                create_tag_version(project_path)
                utils.create_file_modification_times(project_path)
                # copy_project_with_version_control(project_path)
            elif pipeline == "3":
                logger.debug(f"Zinley: Exit now")
                break
    except FileNotFoundError as e:
        logger.error(f"{e}")
        exit()
    except Exception as e:
        logger.info(f"An error occurred while copying the project: {e}")
        switch_tag_version(project_path, get_latest_version(project_path))
        exit()

def get_latest_version(project_path):
    try:
         # Ensure the project path is a Git repository
        if not os.path.exists(os.path.join(project_path, '.git')):
            raise RuntimeError(f"The path {project_path} is not a Git repository.")
        # Get the list of existing tags
        tags = run_git_command('git tag', cwd=project_path).split('\n')
        logger.info(f"tags={tags}")
        latest_version = "v1"
        # if tags not empty or length > 1
        if len(tags) > 2:
            version_numbers = [int(tag[1:]) for tag in tags if tag.startswith('v') and tag[1:].isdigit()]
            prev_version_number = max(version_numbers, default=0) - 1
            latest_version = f"v{prev_version_number}"


        return latest_version
    except Exception as e:
        logger.info(f"Failed to create tag version: {e}")

async def get_prePrompt(user_prompt):
    """Generate idea plans based on user prompt and available files."""
    first_prompt_controller = FirstPromptAgent(max_tokens)
    return await first_prompt_controller.get_prePrompt_plans(user_prompt)

def parse_payload(user_prompt_json, project_path):
    try:
        file_path = None
        data = json.loads(user_prompt_json)
        user_prompt = data.get("prompt", "")
        file_path = data.get("file_path", None)
        if file_path and os.path.exists(file_path):
            logger.info(f"{file_path} exists. Moving the file to {project_path}")
            # Check if the destination file already exists and remove it if necessary
            destination_file = os.path.join(project_path, os.path.basename(file_path))
            if os.path.exists(destination_file):
                os.remove(destination_file)
            shutil.move(file_path, project_path)
        else:
            logger.debug(f"{file_path} does not exists")
            file_path = None
    except json.JSONDecodeError:
        # If input is not valid JSON, treat it as plain text
        user_prompt = user_prompt_json
        logger.info(f"Received Plain Text Prompt: {user_prompt}")
    return user_prompt, file_path

def update_tree(project_path, home_directory, hidden_zinley_folder_name, project_name):
    parts = project_path.split('/')
    project_name = parts[-1]
    output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
    os.makedirs(output_dir, exist_ok=True)

    # Run the `tree` command and save the output to tree.txt, excluding the Zinley folder
    tree_path = os.path.join(output_dir, "tree.txt")

    # Clear the file contents before writing new content
    open(tree_path, 'w').close()

    with open(tree_path, 'w') as f:
        utils.tree(project_path, exclude="Zinley", stdout=f)

    # Need to update the all files modifying time
    utils.create_file_modification_times(project_path)

def get_version(project_path):
    tags = run_git_command('git tag', cwd=project_path).split('\n')
    return tags
