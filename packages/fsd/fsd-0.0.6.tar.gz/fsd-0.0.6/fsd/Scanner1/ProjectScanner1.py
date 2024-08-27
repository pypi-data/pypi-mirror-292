import os
import subprocess
import aiohttp
import asyncio
import sys
import time

from fsd.util import utils
from .ScannerAgent import ScannerAgent
from .DependenciesFinderAgent import DependenciesFinderAgent
from .DependencyAgent import DependencyAgent

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fsd.ResultsManager1 import ResultsManager1
from fsd.log.logger_config import get_logger
logger = get_logger(__name__)

class ProjectScanner1:
    def __init__(self, project_path, api_key, endpoint, deployment_id, max_tokens, max_agents=20):
        self.project_path = project_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.max_agents = max_agents
        self.agents = []
        self.results_manager1 = ResultsManager1()
        self.dependencyFinder = DependenciesFinderAgent(self.project_path, self.api_key, self.endpoint,
                                                        self.deployment_id, self.max_tokens)
        self.dependencyScanner = DependencyAgent(self.project_path, self.api_key, self.endpoint, self.deployment_id,
                                                 self.max_tokens)

    def create_agents(self):
        """Create the specified number of ScannerAgent instances."""
        self.agents = [ScannerAgent(self.project_path, self.api_key, self.endpoint, self.deployment_id, self.max_tokens)
                       for _ in range(self.max_agents)]

    def get_tree_txt_files(self):
        """Scan for tree.txt files in the specified directory."""
        tree_txt_files = []
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = self.project_path.split('/')
        project_name = parts[-1]
        tree_path = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley/Project_analysis")

        if not os.path.exists(tree_path):
            logger.debug(f"Directory does not exist: {tree_path}")
            return tree_txt_files

        for root, _, files in os.walk(tree_path):
            for file in files:
                if file == 'tree.txt':
                    file_path = os.path.join(root, file)
                    tree_txt_files.append(file_path)

        return tree_txt_files

    def get_txt_files(self):
        """Scan for all txt files in the specified directory."""
        txt_files = []
        home_directory = os.path.expanduser('~')
        hidden_zinley_folder_name = '.zinley'
        parts = self.project_path.split('/')
        project_name = parts[-1]
        txt_path = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley/Project_analysis")

        if not os.path.exists(txt_path):
            logger.debug(f"Directory does not exist: {txt_path}")
            return txt_files

        for root, _, files in os.walk(txt_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    txt_files.append(file_path)

        return txt_files

    # async def update_tree(self):
    #     """Update the project directory tree and save to tree.txt."""
    #     tree_path = self.directory_path
    #     output_dir = os.path.join(tree_path, "Zinley", "Project_analysis")
    #     os.makedirs(output_dir, exist_ok=True)
    #     tree_file_path = os.path.join(output_dir, "tree.txt")
    #     # Open the file to write the tree output
    #     with open(tree_file_path, 'w') as f:
    #         # Run the tree command and capture the output
    #         utils.tree(self.directory_path, exclude="Zinley", stdout=f)

    async def update_tree(self):
        """Update the project directory tree and save to tree.txt."""
        try:
            tree_path = self.project_path
            home_directory = os.path.expanduser('~')
            hidden_zinley_folder_name = '.zinley'
            parts = tree_path.split('/')
            project_name = parts[-1]
            output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley",
                                      "Project_analysis")
            os.makedirs(output_dir, exist_ok=True)
            tree_file_path = os.path.join(output_dir, "tree.txt")

            with open(tree_file_path, 'w') as f:
                utils.tree(self.project_path, exclude="Zinley", stdout=f)

        except Exception as e:
            logger.info(f"Failed to update tree: {e}")

    async def get_dependency_files(self, tree):
        """Generate replacing plans based on user prompt and available files."""
        return await self.dependencyFinder.get_file_plannings(tree)

    async def get_dependency_context(self, dependency_files):
        """Generate replacing plans based on user prompt and available files."""
        return await self.dependencyScanner.get_file_plannings(dependency_files)

    async def list_dependencies(self):
        """List all dependencies for the project by scanning the project files and checking for installed dependencies."""

        await self.update_tree()
        tree = self.get_tree_txt_files()
        file_result = await self.get_dependency_files(tree)
        dependency_files = file_result.get('dependency_files', [])
        if dependency_files:
            result = await self.get_dependency_context(dependency_files)
            return result

        return "No dependencies have been installed yet!"

    def scan_project_files(self):
        """Scan the project directory for all coding files, ignoring images, videos, third-party dependencies, and IDE files."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', '.ico', '.webp'}
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'}

        ignore_dirs = {
            'node_modules', 'venv', '.venv', 'env', '.env', 'vendor', 'Pods', 'Carthage', '.git',
            '.idea', '.vscode', '__pycache__', 'build', 'dist', '.gradle', '.m2', '.bundle',
            '.cxx', 'DerivedData', 'Assets.xcassets', 'Preview Assets.xcassets', 'xcuserdata', 'xcshareddata', 'Zinley'
        }

        ignore_files = {
            '.gitignore', '.gitattributes', 'LICENSE', 'yarn.lock', 'package-lock.json',
            'Pipfile.lock', '.DS_Store', '.env', 'Gemfile.lock', 'Cargo.lock', '.classpath',
            '.project', 'Thumbs.db', 'npm-debug.log', 'pip-log.txt', '.metadata', '.pbxproj', '.xcworkspace',
            '.DS_Store', '.xcodeproj'
        }

        code_extensions = {
            # Programming languages
            '.py', '.pyc', '.pyo', '.pyw', '.pyx', '.pxd', '.pyd',  # Python
            '.js', '.jsx', '.ts', '.tsx',  # JavaScript/TypeScript
            '.java', '.class', '.jar',  # Java
            '.c', '.h', '.cpp', '.hpp', '.cc', '.cxx', '.hh', '.hxx', '.ino',  # C/C++
            '.cs', '.csproj',  # C#
            '.go',  # Go
            '.rb', '.rbw', '.rake', '.gemspec', '.rhtml',  # Ruby
            '.php', '.phtml', '.php3', '.php4', '.php5', '.php7', '.phps', '.phpt',  # PHP
            '.kt', '.kts',  # Kotlin
            '.swift',  # Swift
            '.m', '.mm',  # Objective-C
            '.r', '.rdata', '.rds', '.rda', '.rproj',  # R
            '.pl', '.pm', '.t',  # Perl
            '.sh', '.bash', '.bats', '.zsh', '.ksh', '.csh',  # Shell scripts
            '.lua',  # Lua
            '.erl', '.hrl', '.beam',  # Erlang
            '.ex', '.exs',  # Elixir
            '.ml', '.mli', '.fs', '.fsi', '.fsx', '.fsscript',  # OCaml/F#
            '.scala', '.sbt', '.sc',  # Scala
            '.jl',  # Julia
            '.hs', '.lhs',  # Haskell
            '.clj', '.cljs', '.cljc', '.edn',  # Clojure
            '.groovy', '.gvy', '.gy', '.gsh',  # Groovy
            '.v', '.vh', '.sv', '.svh',  # Verilog/SystemVerilog
            '.vhd', '.vhdl',  # VHDL
            '.adb', '.ads', '.ada',  # Ada
            '.d', '.di',  # D
            '.nim', '.nims',  # Nim
            '.rs', '.rlib',  # Rust
            '.cr',  # Crystal
            '.cmake', '.make', '.mak', '.mk',  # Build files
            '.bat', '.cmd',  # Batch files
            # Markup and stylesheets
            '.html', '.htm', '.xhtml', '.jhtml',  # HTML
            '.css', '.scss', '.sass', '.less',  # CSS and preprocessors
            '.xml', '.xsl', '.xslt', '.xsd', '.dtd', '.wsdl',  # XML
            '.md', '.markdown', '.mdown', '.mkdn', '.mkd', '.rst', '.adoc', '.asciidoc',
            # Markdown/AsciiDoc/ReStructuredText
            # Configuration files
            '.json', '.yml', '.yaml', '.ini', '.cfg', '.conf', '.toml', '.plist', '.env', '.editorconfig',
            '.eslintrc', '.prettierrc', '.babelrc', '.stylelintrc', '.dockerfile', '.dockerignore',
            '.gitlab-ci.yml', '.travis.yml', '.circleci/config.yml',
            # Data files
            '.csv', '.tsv', '.parquet', '.avro', '.orc', '.json', '.xml',
            # iOS-specific
            '.nib', '.xib', '.storyboard',  # iOS
            # Android-specific
            '.gradle', '.pro', '.aidl', '.rs', '.rsh', '.xml',
            # Desktop app specific
            '.desktop', '.manifest', '.rc', '.resx', '.xaml', '.appxmanifest', '.csproj', '.vbproj',
            # Web app specific
            '.asp', '.aspx', '.ejs', '.hbs', '.jsp', '.jspx', '.php', '.cfm',
            # Database related
            '.sql', '.db', '.db3', '.sqlite', '.sqlite3', '.rdb', '.mdb', '.accdb', '.pdb',
            # Others
            '.tex', '.bib', '.log', '.txt'
        }

        files_list = []

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d.lower() not in {dir_name.lower() for dir_name in ignore_dirs}]

            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                file_name = os.path.basename(file).lower()

                if file_ext in image_extensions or file_ext in video_extensions or file_name in ignore_files or file_ext not in code_extensions:
                    continue

                files_list.append(file)

        return files_list

    async def scanner(self, file, agent):
        """Generate idea plans based on user prompt and available files."""
        return await agent.get_file_summaries(file)

    async def scan_files_with_agents(self, files):
        """Distribute files among agents and scan them."""
        # Step to remove all empty files from the list
        files = [file for file in files if file]

        logger.debug(f"Final touching: {files}")
        tasks = []
        num_files = len(files)
        num_agents = min(self.max_agents, num_files)

        self.create_agents()

        for i in range(num_files):
            agent = self.agents[i % num_agents]
            tasks.append(self.scanner(files[i], agent))

        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                self.results_manager1.update_results(self.project_path, result[0]['file_path'], result[0]['summary'] + ",definitions_in_file:" + result[0]['ast'])
            except Exception as e:
                logger.info(f"Error processing file with agent: {e}")

    async def scan_total_files_with_agents(self, files):
        """Distribute files among agents and scan them."""
        # Step to remove all empty files from the list
        files = [file for file in files if file]
        logger.info(f"Final touching: {files}")
        tasks = []
        num_files = len(files)
        num_agents = min(self.max_agents, num_files)

        self.create_agents()

        for i in range(num_files):
            agent = self.agents[i % num_agents]
            tasks.append(self.scanner(files[i], agent))

        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                self.results_manager1.update_total_results(self.project_path, result[0]['file_path'],
                                                           result[0]['summary'])
            except Exception as e:
                logger.info(f"Error processing file with agent: {e}")

    async def get_started(self):
        logger.info("Start scanning")
        start_time = time.time()
        try:
            await self.update_tree()
            files = self.scan_project_files()
            files = [file for file in files if file]
            dependencies = await self.list_dependencies()
            self.results_manager1.update_dependencies_results(self.project_path, dependencies)
            await self.scan_total_files_with_agents(files)
            logger.info("Done scanning")
        except Exception as e:
            logger.info(f"Error during scanning process: {e}")
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Scanning completed in {duration:.2f} seconds")

    async def scanning_files(self, files):
        logger.info("Start scanning")
        start_time = time.time()
        try:
            await self.update_tree()
            dependencies = await self.list_dependencies()
            self.results_manager1.update_dependencies_results(self.project_path, dependencies)
            await self.scan_files_with_agents(files)
            logger.info("Done scanning")
        except Exception as e:
            logger.info(f"Error during scanning process: {e}")
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Scanning completed in {duration:.2f} seconds")

    async def get_incremental_scan_started(self, files):
        logger.info("Start incremental scanning")
        start_time = time.time()
        try:
            await self.update_tree()
            dependencies = await self.list_dependencies()
            self.results_manager1.update_dependencies_results(self.project_path, dependencies)
            await self.scan_files_with_agents(files)
            logger.info("Done incremental scanning")
        except Exception as e:
            logger.info(f"Error during incremental scanning process: {e}")
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Incremental Scanning completed in {duration:.2f} seconds")

