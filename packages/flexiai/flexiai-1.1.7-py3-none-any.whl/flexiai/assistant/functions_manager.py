# flexiai/assistant/functions_manager.py
import logging
from flexiai.core.flexi_managers.multi_agent_system import MultiAgentSystemManager
from flexiai.core.flexi_managers.run_manager import RunManager

logger = logging.getLogger(__name__)


class FunctionsManager:
    """
    FunctionsManager handles core functionality for RAG operations, such as saving/loading content,
    continuing conversations with assistants, and initializing agents.
    """

    def __init__(self, multi_agent_system: MultiAgentSystemManager, run_manager: RunManager):
        """
        Initializes the FunctionsManager with necessary dependencies.
        """
        self.multi_agent_system = multi_agent_system
        self.run_manager = run_manager


    def save_processed_content(self, from_assistant_id, to_assistant_id, processed_content):
        """
        Saves the processed user content for RAG purposes, allowing AI assistants to 
        store and retrieve contextual information.
        """
        return self.multi_agent_system.save_processed_content(from_assistant_id, to_assistant_id, processed_content)


    def load_processed_content(self, from_assistant_id, to_assistant_id, multiple_retrieval=False):
        """
        Loads the stored processed user content, enabling AI assistants to access 
        previously stored information for enhanced context and continuity in RAG.
        """
        return self.multi_agent_system.load_processed_content(from_assistant_id, to_assistant_id, multiple_retrieval)


    def continue_conversation_with_assistant(self, assistant_id, user_content):
        """
        Continues the conversation with an assistant by submitting user content 
        and managing the resulting run, allowing dynamic and contextually aware interactions.
        """
        return self.multi_agent_system.continue_conversation_with_assistant(assistant_id, user_content)


    def initialize_agent(self, assistant_id):
        """
        Initializes an agent for the given assistant ID. If a thread already exists for the assistant ID,
        it returns a message indicating the existing thread. Otherwise, it creates a new thread.
        """
        return self.multi_agent_system.initialize_agent(assistant_id)
