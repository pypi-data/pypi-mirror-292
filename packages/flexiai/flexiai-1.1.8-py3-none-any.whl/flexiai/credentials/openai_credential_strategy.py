# flexiai/credentials/openai_credential_strategy.py
import os
from openai import OpenAI
from flexiai.config.config import config
from flexiai.credentials.credential_strategy import CredentialStrategy

class OpenAICredentialStrategy(CredentialStrategy):
    """
    Credential strategy for OpenAI.
    
    This class implements the CredentialStrategy interface to provide an OpenAI client
    initialized with the necessary API key and headers.
    """
    
    def get_client(self):
        """
        Get the OpenAI client.
        
        This method retrieves the OpenAI API key, organization ID, project ID, and assistant version from
        environment variables or the configuration, sets up the necessary headers, 
        and returns an OpenAI client instance.
        
        Returns:
            OpenAI: The initialized OpenAI client.
        
        Raises:
            ValueError: If the OpenAI API key is not set.
        """
        api_key = os.getenv("OPENAI_API_KEY", config.OPENAI_API_KEY)
        organization_id = os.getenv("OPENAI_ORGANIZATION_ID", config.OPENAI_ORGANIZATION_ID)
        project_id = os.getenv("OPENAI_PROJECT_ID", config.OPENAI_PROJECT_ID)
        api_version = os.getenv("OPENAI_API_VERSION", config.OPENAI_API_VERSION)
        assistant_version = os.getenv("OPENAI_ASSISTANT_VERSION", config.OPENAI_ASSISTANT_VERSION)

        if not api_key:
            raise ValueError("OpenAI API key is not set.")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "OpenAI-Organization": organization_id,
            "OpenAI-Project": project_id,
            "OpenAI-Version": api_version,
            "OpenAI-Beta": f"assistants={assistant_version}"
        }
        
        return OpenAI(api_key=api_key, default_headers=headers)
