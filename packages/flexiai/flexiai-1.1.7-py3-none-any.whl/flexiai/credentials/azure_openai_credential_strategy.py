# flexiai/credentials/azure_openai_credential_strategy.py
import os
from openai import AzureOpenAI
from flexiai.config.config import config
from flexiai.credentials.credential_strategy import CredentialStrategy

class AzureOpenAICredentialStrategy(CredentialStrategy):
    """
    Credential strategy for Azure OpenAI.
    
    This class implements the CredentialStrategy interface to provide an Azure OpenAI client
    initialized with the necessary API key, endpoint, and API version.
    """
    
    def get_client(self):
        """
        Get the Azure OpenAI client.
        
        This method retrieves the Azure OpenAI API key, endpoint, and API version from 
        environment variables or the configuration and returns an Azure OpenAI client instance.
        
        Returns:
            AzureOpenAI: The initialized Azure OpenAI client.
        
        Raises:
            ValueError: If the Azure OpenAI API key, endpoint, or API version is not set.
        """
        api_key = os.getenv("AZURE_OPENAI_API_KEY", config.AZURE_OPENAI_API_KEY)
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", config.AZURE_OPENAI_ENDPOINT)
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", config.AZURE_OPENAI_API_VERSION)
        
        if not api_key or not azure_endpoint or not api_version:
            raise ValueError("Azure OpenAI API key, endpoint, or API version is not set.")
        
        return AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
