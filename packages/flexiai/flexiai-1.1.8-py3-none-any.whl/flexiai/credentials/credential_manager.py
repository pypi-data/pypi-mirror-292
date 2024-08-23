# flexiai/credentials/credential_manager.py
from flexiai.config.config import config
from flexiai.credentials.azure_openai_credential_strategy import AzureOpenAICredentialStrategy
from flexiai.credentials.openai_credential_strategy import OpenAICredentialStrategy

class CredentialManager:
    """
    Manages the credentials and provides the appropriate client based on the credential type.
    """
    def __init__(self):
        self.credential_type = config.CREDENTIAL_TYPE
        self.client = self._get_client()

    def _get_client(self):
        if self.credential_type == 'openai':
            strategy = OpenAICredentialStrategy()
        elif self.credential_type == 'azure':
            strategy = AzureOpenAICredentialStrategy()
        else:
            raise ValueError(f"Unsupported credential type: {self.credential_type}")

        return strategy.get_client()
