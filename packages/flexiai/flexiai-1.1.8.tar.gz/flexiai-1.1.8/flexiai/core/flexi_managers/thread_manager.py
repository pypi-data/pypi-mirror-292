# flexiai/core/thread_manager.py
from openai import OpenAIError


class ThreadManager:
    """
    ThreadManager handles the creation of new threads using the OpenAI or Azure OpenAI API.

    Attributes:
        client (OpenAI or AzureOpenAI): The client for interacting with OpenAI or Azure OpenAI services.
        logger (logging.Logger): The logger for logging information and errors.
    """

    def __init__(self, client, logger):
        self.client = client
        self.logger = logger


    def create_thread(self):
        """
        Creates a new thread.

        Returns:
            object: The thread object.

        Raises:
            OpenAIError: If the API call to create a new thread fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info("Creating a new thread")
            thread = self.client.beta.threads.create()
            self.logger.info(f"Created thread with ID: {thread.id}")
            return thread
        except OpenAIError as e:
            self.logger.error(f"Failed to create a new thread: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while creating a thread: {str(e)}", exc_info=True)
            raise


    def retrieve_thread(self, thread_id):
        """
        Retrieves details of a specific thread by its ID.

        Args:
            thread_id (str): The ID of the thread to retrieve.

        Returns:
            object: The thread object.

        Raises:
            OpenAIError: If the API call to retrieve the thread fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Retrieving details for thread ID: {thread_id}")
            thread = self.client.beta.threads.retrieve(thread_id=thread_id)
            self.logger.info(f"Retrieved details for thread ID: {thread.id}")
            return thread
        except OpenAIError as e:
            self.logger.error(f"Failed to retrieve thread details: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while retrieving thread details: {str(e)}", exc_info=True)
            raise


    def update_thread(self, thread_id, metadata=None, tool_resources=None):
        """
        Updates a thread with the given details.

        Args:
            thread_id (str): The ID of the thread to update.
            metadata (dict, optional): Metadata to update for the thread.
            tool_resources (dict, optional): Tool resources to update for the thread.

        Returns:
            object: The updated thread object.

        Raises:
            OpenAIError: If the API call to update the thread fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Updating thread ID: {thread_id} with metadata: {metadata} and tool_resources: {tool_resources}")
            thread = self.client.beta.threads.update(thread_id=thread_id, metadata=metadata, tool_resources=tool_resources)
            self.logger.info(f"Updated thread ID: {thread.id}")
            return thread
        except OpenAIError as e:
            self.logger.error(f"Failed to update thread: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while updating thread: {str(e)}", exc_info=True)
            raise


    def delete_thread(self, thread_id):
        """
        Deletes a thread by its ID.

        Args:
            thread_id (str): The ID of the thread to delete.

        Returns:
            bool: True if the thread was deleted successfully, False otherwise.

        Raises:
            OpenAIError: If the API call to delete the thread fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Deleting thread ID: {thread_id}")
            self.client.beta.threads.delete(thread_id=thread_id)
            self.logger.info(f"Deleted thread ID: {thread_id}")
            return True
        except OpenAIError as e:
            self.logger.error(f"Failed to delete thread: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while deleting thread: {str(e)}", exc_info=True)
            raise


    def attach_assistant_to_thread(self, assistant_id, thread_id):
        """
        Attaches an assistant to an existing thread.

        Args:
            assistant_id (str): The ID of the assistant.
            thread_id (str): The ID of the thread.

        Returns:
            object: The run object indicating the assistant has been attached.

        Raises:
            OpenAIError: If the API call to attach the assistant fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Attaching assistant ID: {assistant_id} to thread ID: {thread_id}")
            run = self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
            self.logger.info(f"Attached assistant ID: {assistant_id} to thread ID: {thread_id}")
            return run
        except OpenAIError as e:
            self.logger.error(f"Failed to attach assistant ID {assistant_id} to thread ID {thread_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while attaching assistant ID {assistant_id} to thread ID {thread_id}: {str(e)}", exc_info=True)
            raise
