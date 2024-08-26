import os
from datetime import datetime
import re
import json
import subprocess
import random
import shutil
import sys

from util.tree import Tree
from log.logger_config import get_logger
logger = get_logger(__name__)

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', '.ico', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'}

IGNORE_DIRS = {
    'node_modules', 'venv', '.venv', 'env', '.env', 'vendor', 'Pods', 'Carthage', '.git',
    '.idea', '.vscode', '__pycache__', 'build', 'dist', '.gradle', '.m2', '.bundle',
    '.cxx', 'DerivedData', 'Assets.xcassets', 'Preview Assets.xcassets', 'xcuserdata', 'xcshareddata', 'Zinley'
}

IGNORE_FILES = {
    '.gitignore', '.gitattributes', 'README.md', 'LICENSE', 'yarn.lock', 'package-lock.json',
    'Pipfile.lock', '.DS_Store', '.env', 'Gemfile.lock', 'Cargo.lock', '.classpath',
    '.project', 'Thumbs.db', 'npm-debug.log', 'pip-log.txt', '.metadata', '.pbxproj', '.xcworkspace', '.DS_Store',
    '.xcodeproj', 'file_modification_times.txt'
}

CODE_EXTENSIONS = {
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
    '.md', '.markdown', '.mdown', '.mkdn', '.mkd', '.rst', '.adoc', '.asciidoc',  # Markdown/AsciiDoc/ReStructuredText
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


def get_current_time_formatted():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%m/%d/%y")
    return formatted_time


def clean_json(json_str):
    original = json_str
    attempt_count = 20  # Number of attempts to fix JSON
    attempt = 0

    while attempt < attempt_count:
        attempt += 1
        try:
            # Check and remove markdown for JSON
            if re.match(r'```json\s*', json_str) and re.search(r'```\s*$', json_str):
                json_str = re.sub(r'```json\s*', '', json_str)  # Remove starting markdown ```json
                json_str = re.sub(r'```\s*$', '', json_str)  # Remove ending markdown ```

            # Fix escaping characters for JSON
            json_str = re.sub(r'(?<!\\)\\', r'\\\\', json_str)  # Fix single backslashes
            json_str = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_str)  # Fix other escape sequences

            # Attempt to parse the JSON to verify if it's valid
            json_obj = json.loads(json_str)
            json_str = json.dumps(json_obj, indent=4)
            return {"status": "success", "cleaned_json": json_str}

        except json.JSONDecodeError as e:
            if attempt == attempt_count:
                return {"status": "error", "error_message": str(e), "original": original}

            try:
                # "Expecting , delimiter: line 34 column 54 (char 1158)"
                # position of unexpected character after '"'
                unexp = int(re.findall(r'\(char (\d+)\)', str(e))[0])
                # position of unescaped '"' before that
                unesc = json_str.rfind(r'"', 0, unexp)
                json_str = json_str[:unesc] + r'\"' + json_str[unesc + 1:]
                # position of corresponding closing '"' (+2 for inserted '\')
                closg = json_str.find(r'"', unesc + 2)
                json_str = json_str[:closg] + r'\"' + json_str[closg + 1:]
            except Exception as inner_e:
                return {"status": "error", "error_message": str(inner_e), "original": original}

    return {"status": "error", "error_message": "Reached maximum attempts", "original": original}


# Remove all empty spaces to make things easier below
def remove_spaces(json_str):
    json_str = json_str.replace('" :', '":').replace(': "', ':"').replace('"\n', '"').replace('" ,', '",').replace(
        ', "', ',"')
    # First remove the " from where it is supposed to be.
    json_str = re.sub(r'\\"', '"', json_str)
    json_str = re.sub(r'{"', '{`', json_str)
    json_str = re.sub(r'"}', '`}', json_str)
    json_str = re.sub(r'":"', '`:`', json_str)
    json_str = re.sub(r'":\[', '`:[', json_str)
    json_str = re.sub(r'":\{', '`:{', json_str)
    json_str = re.sub(r'":([0-9]+)', '`:\\1', json_str)
    json_str = re.sub(r'":(null|true|false)', '`:\\1', json_str)
    json_str = re.sub(r'","', '`,`', json_str)
    json_str = re.sub(r'",\[', '`,[', json_str)
    json_str = re.sub(r'",\{', '`,{', json_str)
    json_str = re.sub(r',"', ',`', json_str)
    json_str = re.sub(r'\["', '[`', json_str)
    json_str = re.sub(r'"\]', '`]', json_str)
    # Backslash all double quotes (")
    json_str = re.sub(r'"', '\\"', json_str)
    # Put back all the " where it is supposed to be.
    json_str = re.sub(r'\`', '\"', json_str)
    return json_str


# Combine both functions
def combined_clean_json(json_str):
    cleaned_str = clean_json(json_str)
    if cleaned_str["status"] == "success":
        cleaned_str["cleaned_json"] = remove_spaces(cleaned_str["cleaned_json"])
    return cleaned_str


def return_original_error(original):
    try:
        json_obj = json.loads(original)
        json_str = json.dumps(json_obj, indent=4)
        return {"status": "success", "cleaned_json": original}
    except json.JSONDecodeError as e:
        return {"status": "error", "error_message": str(e)}


def split_messages(messages, max_length):
    """
    Splits the messages into chunks that fit within the maximum token length.

    Args:
        messages (list): List of messages.
        max_length (int): Maximum length of tokens.

    Returns:
        list: List of message chunks.
    """
    chunks = []
    current_chunk = []
    current_length = 0

    for message in messages:
        message_length = len(message['content'].split())
        if current_length + message_length > max_length:
            chunks.append(current_chunk)
            current_chunk = []
            current_length = 0

        current_chunk.append(message)
        current_length += message_length

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def get_available_simulator_details():
    try:
        # Run the xcrun command to get a list of simulators in JSON format
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "--json"],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse the JSON output
        devices = json.loads(result.stdout)

        # Extract detailed information of the available iOS simulators
        available_simulator_details = []
        for device_type in devices['devices']:
            # Filter for iOS simulators only
            if 'iOS' in device_type:
                for device in devices['devices'][device_type]:
                    if device.get('isAvailable', False):
                        details = {
                            'name': device.get('name', 'Unknown'),
                            'state': device.get('state', 'Unknown'),
                            'udid': device.get('udid', 'Unknown'),
                            'device_type': device_type
                        }
                        available_simulator_details.append(details)

        return available_simulator_details

    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while fetching the simulator details: {e}")
        return []


def get_preferred_simulator_uuid():
    available_simulators = get_available_simulator_details()

    # Filter for booted simulators
    booted_simulators = [sim for sim in available_simulators if sim['state'] == 'Booted']

    if booted_simulators:
        chosen = random.choice(booted_simulators)
        logger.debug(f"Using: {chosen}")
        udid = chosen['udid']
        return udid

    # If no simulators are booted, filter for shutdown simulators in the iPhone range
    shutdown_iphones = [sim for sim in available_simulators if sim['state'] == 'Shutdown' and 'iPhone' in sim['name']]

    if shutdown_iphones:
        chosen = random.choice(shutdown_iphones)
        logger.debug(f"Using: {chosen}")
        udid = chosen['udid']
        return udid

    return None


def create_file_modification_times(project_path):
    file_mod_times = []
    for root, _, files in os.walk(project_path):
        for file in files:
            filepath = os.path.join(root, file)
            mod_time = subprocess.check_output(['stat', '-f', '%Sm %N', filepath]).decode('utf-8').strip()
            file_mod_times.append(mod_time)
    home_directory = os.path.expanduser('~')
    hidden_zinley_folder_name = '.zinley'
    parts = project_path.split('/')
    project_name = parts[-1]
    with open(os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis", "file_modification_times.txt"), "w") as f:
        for line in file_mod_times:
            f.write(line + '\n')


def get_new_or_modified_file(project_path):
    home_directory = os.path.expanduser('~')
    hidden_zinley_folder_name = '.zinley'
    parts = project_path.split('/')
    project_name = parts[-1]
    output_dir = os.path.join(home_directory, hidden_zinley_folder_name, project_name, "Zinley", "Project_analysis")
    previous_file_mod_times = set(
        read_file_lines(os.path.join(output_dir, "file_modification_times.txt")))

    current_file_mod_times = set()
    for root, _, files in os.walk(project_path):
        for file in files:
            filepath = os.path.join(root, file)
            mod_time = subprocess.check_output(['stat', '-f', '%Sm %N', filepath]).decode('utf-8').strip()
            current_file_mod_times.add(mod_time)

    diff_files = current_file_mod_times - previous_file_mod_times
    ret = []
    for f in diff_files:
        file_path = f.split(" ")[-1]
        file = os.path.basename(file_path)
        file_ext = os.path.splitext(file)[1]
        file_name = os.path.basename(file)

        if (file_ext in IMAGE_EXTENSIONS or file_ext in VIDEO_EXTENSIONS or file_name in IGNORE_FILES or
                file_ext not in CODE_EXTENSIONS):
            continue
        ret.append(file)
    return ret


def read_file_lines(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def tree(project_path, exclude = "", stdout = sys.stdout):
    t = Tree()
    t.walk(project_path, exclude = exclude, stdout = stdout)
    print(t.summary(), file = stdout, flush=True)