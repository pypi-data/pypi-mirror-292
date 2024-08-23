# flexiai/scripts/flexiai_rag_extension.py
import os
from pathlib import Path

def _detect_project_root():
    """
    Detects the project root directory based on a known file or structure.

    Returns:
        str: The detected project root directory path.
    """
    current_dir = Path.cwd()
    project_root = current_dir
    return str(project_root)

def create_logs_folder(project_root):
    log_folder = os.path.join(project_root, 'logs')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
        print(f"Created directory: {log_folder}")

def create_user_flexiai_rag_folder(project_root):
    dst_folder = os.path.join(project_root, 'user_flexiai_rag')
    data_folder = os.path.join(dst_folder, 'data')

    # List of subdirectories to create inside 'data'
    data_subfolders = ['audio', 'csv', 'images', 'vectors_store']

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        print(f"Created directory: {data_folder}")
    
    # Create the subdirectories under 'data'
    for subfolder in data_subfolders:
        subfolder_path = os.path.join(data_folder, subfolder)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
            print(f"Created directory: {subfolder_path}")
    
    files_content = {
        '__init__.py': "# user_flexiai_rag/__init__.py\n",
        'user_functions_mapping.py': '''# user_flexiai_rag/user_functions_mapping.py
import logging
from user_flexiai_rag.user_functions_manager import FunctionsManager

logger = logging.getLogger(__name__)

async def map_user_functions():
    """
    Maps user-defined functions to FlexiAI asynchronously and efficiently, ready for future calls.
    
    This function should be awaited when called by the FunctionMapping class.
    """
    logger.info("Mapping user-defined functions...")

    # Initialize the FunctionsManager
    user_functions_manager = FunctionsManager()

    # Map user-defined personal and assistant functions
    user_personal_functions = {
        'search_youtube': user_functions_manager.search_youtube,
    }

    user_assistant_functions = {
        #  Functions to call other assistants, must end with '_assistant'
    }

    logger.info(f"User personal functions are: {list(user_personal_functions.keys())}")
    logger.info(f"User assistant functions are: {list(user_assistant_functions.keys())}")

    # Return the mappings
    return user_personal_functions, user_assistant_functions
''',
        'user_functions_manager.py': '''# user_flexiai_rag/user_functions_manager.py
import logging
import urllib.parse
import subprocess

class FunctionsManager:
    """
    FunctionsManager handles user-defined tasks, enabling RAG capabilities, interactions,
    and async operations for tasks such as saving/loading content, initializing agents,
    and YouTube searches.
    """

    def __init__(self):
        """
        Initializes the FunctionsManager instance.
        """
        self.logger = logging.getLogger(__name__)


    def search_youtube(self, query):
        """
        Searches YouTube for the given query and opens the search results page
        in the default web browser. This function demonstrates integration with 
        external services as part of RAG capabilities.

        Args:
            query (str): The search query string.

        Returns:
            dict: A dictionary containing the status, message, and result (URL)
        """
        self.logger.info(f"Executing search on YouTube with query: {query}")

        if not query:
            return {
                "status": False,
                "message": "Query cannot be empty.",
                "result": None
            }

        try:
            query_encoded = urllib.parse.quote(query)
            youtube_search_url = f"https://www.youtube.com/results?search_query={query_encoded}"
            self.logger.info(f"Opening YouTube search for query: {query}")

            subprocess.run(['powershell.exe', '-Command', 'Start-Process', youtube_search_url], check=True)
            self.logger.info("YouTube search page opened successfully.")
            return {
                "status": True,
                "message": "YouTube search page opened successfully.",
                "result": youtube_search_url
            }
        except subprocess.CalledProcessError as e:
            error_message = f"Subprocess error: {str(e)}"
            self.logger.error(error_message, exc_info=True)
            return {
                "status": False,
                "message": error_message,
                "result": None
            }
        except Exception as e:
            error_message = f"Failed to open YouTube search for query: {query}. Error: {str(e)}"
            self.logger.error(error_message, exc_info=True)
            return {
                "status": False,
                "message": error_message,
                "result": None
            }

    # Add your other functions to be used by assistants. Functions are of these types:
    # - personal functions: functions used by your assistant for personal tasks (execute actions 
    #                       or gather information to provide accurate results)
    # - assistant functions: functions that call other assistants in the Multi-Agent System, 
    #                        must end with '_assistant'

''',
    }

    for filename, content in files_content.items():
        file_path = os.path.join(dst_folder, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Created file: {file_path}")

def create_env_file(project_root):
    env_file = os.path.join(project_root, '.env')
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write(
                "# ============================================================================================ #\n"
                "#                                      OpenAI Configuration                                    #\n"
                "# ============================================================================================ #\n"
                "# Replace 'your_openai_api_key_here' with your actual OpenAI API key.\n"
                "OPENAI_API_KEY=your_openai_api_key_here\n\n"
                "# Replace 'your_openai_api_version_here' with your actual OpenAI API version.\n"
                "# Example for OpenAI: 2020-11-07\n"
                "OPENAI_API_VERSION=your_openai_api_version_here\n\n"
                "# Replace 'your_openai_organization_id_here' with your actual OpenAI Organization ID.\n"
                "OPENAI_ORGANIZATION_ID=your_openai_organization_id_here\n\n"
                "# Replace 'your_openai_project_id_here' with your actual OpenAI Project ID.\n"
                "OPENAI_PROJECT_ID=your_openai_project_id_here\n\n"
                "# Replace 'your_openai_assistant_version_here' with your actual OpenAI Assistant version.\n"
                "# Example for Assistant: v1 or v2\n"
                "OPENAI_ASSISTANT_VERSION=your_openai_assistant_version_here\n\n\n"
                "# ============================================================================================ #\n"
                "#                                      Azure OpenAI Configuration                              #\n"
                "# ============================================================================================ #\n"
                "# Replace 'your_azure_openai_api_key_here' with your actual Azure OpenAI API key.\n"
                "AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here\n\n"
                "# Replace 'your_azure_openai_endpoint_here' with your actual Azure OpenAI endpoint.\n"
                "AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here\n\n"
                "# Replace 'your_azure_openai_api_version_here' with your actual Azure OpenAI API version.\n"
                "# Example for Azure: 2024-05-01-preview\n"
                "AZURE_OPENAI_API_VERSION=your_azure_openai_api_version_here\n\n\n"
                "# ============================================================================================ #\n"
                "#                                      General Configuration                                   #\n"
                "# ============================================================================================ #\n"
                "# Set this to 'openai' if you are using OpenAI, or 'azure' if you are using Azure OpenAI.\n"
                "CREDENTIAL_TYPE=openai\n\n"
                "# ============================================================================================ #\n"
                "#                                      User Project Configuration                              #\n"
                "# ============================================================================================ #\n"
                "# Define the root directory of the user's project to integrate custom functions into FlexiAI.\n"
                "USER_PROJECT_ROOT_DIR=/your/path/to_your/project_root_directory\n\n"
            )
        print(f"Created file: {env_file}")

def create_requirements_file(project_root):
    requirements_file = os.path.join(project_root, 'requirements.txt')
    if not os.path.exists(requirements_file):
        with open(requirements_file, 'w') as f:
            f.write(
                "annotated-types==0.7.0\n"
                "anyio==4.4.0\n"
                "azure-common==1.1.28\n"
                "azure-core==1.30.2\n"
                "azure-identity==1.17.1\n"
                "azure-mgmt-core==1.4.0\n"
                "azure-mgmt-resource==23.1.1\n"
                "bleach==6.1.0\n"
                "certifi==2024.7.4\n"
                "cffi==1.16.0\n"
                "charset-normalizer==3.3.2\n"
                "click==8.1.7\n"
                "cryptography==43.0.0\n"
                "Flask==3.0.3\n"
                "h11==0.14.0\n"
                "httpcore==1.0.5\n"
                "httpx==0.27.0\n"
                "idna==3.7\n"
                "iniconfig==2.0.0\n"
                "isodate==0.6.1\n"
                "itsdangerous==2.2.0\n"
                "Jinja2==3.1.4\n"
                "MarkupSafe==2.1.5\n"
                "msal==1.30.0\n"
                "msal-extensions==1.2.0\n"
                "nest-asyncio==1.6.0\n"
                "openai==1.40.2\n"
                "packaging==24.1\n"
                "platformdirs==3.7.0\n"
                "pluggy==1.5.0\n"
                "portalocker==2.10.1\n"
                "pycparser==2.22\n"
                "pydantic==2.8.2\n"
                "pydantic-settings==2.3.3\n"
                "pydantic_core==2.20.1\n"
                "PyJWT==2.8.0\n"
                "pytest==8.3.1\n"
                "python-dotenv==1.0.1\n"
                "requests==2.32.3\n"
                "six==1.16.0\n"
                "sniffio==1.3.1\n"
                "tqdm==4.66.4\n"
                "typing_extensions==4.12.2\n"
                "urllib3==2.2.2\n"
                "Werkzeug==3.0.3\n"
            )
        print(f"Created file: {requirements_file}")

def setup_project():
    project_root = _detect_project_root()
    create_logs_folder(project_root)
    create_user_flexiai_rag_folder(project_root)
    create_env_file(project_root)
    create_requirements_file(project_root)

if __name__ == '__main__':
    setup_project()
