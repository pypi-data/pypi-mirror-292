# flexiai/credentials/credential_strategy.py
from abc import ABC, abstractmethod

class CredentialStrategy(ABC):
    """
    Abstract base class for credential strategies. This class defines the interface
    for different credential strategies to get their respective API clients.
    """
    
    @abstractmethod
    def get_client(self):
        """
        Abstract method to get the API client.
        
        This method should be implemented by all subclasses to return the appropriate
        client for the given credential strategy.
        
        Returns:
            Client: The API client for the specific credential strategy.
        """
        pass
