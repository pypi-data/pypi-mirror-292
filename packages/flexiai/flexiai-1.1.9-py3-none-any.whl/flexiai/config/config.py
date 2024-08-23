# flexiai/config/config.py 
import logging
from dotenv import load_dotenv
from pydantic import ValidationError
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Config(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_API_VERSION: str
    OPENAI_ORGANIZATION_ID: str
    OPENAI_PROJECT_ID: str
    OPENAI_ASSISTANT_VERSION: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str
    CREDENTIAL_TYPE: str
    USER_PROJECT_ROOT_DIR: str
    
    class Config:
        env_file = ".env"

# Initialize logger
logger = logging.getLogger(__name__)

try:
    # Attempt to load the configuration
    config = Config()
    logger.info("Configuration loaded successfully.")
except ValidationError as e:
    # Log and raise an error if configuration validation fails
    logger.error(f"Configuration validation error: {str(e)}", exc_info=True)
    raise RuntimeError("Environment variable validation failed. Please check your .env file and ensure all variables are set correctly.") from e
