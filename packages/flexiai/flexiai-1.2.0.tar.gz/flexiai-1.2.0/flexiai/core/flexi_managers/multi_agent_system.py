# flexiai/core/flexi_managers/multi_agent_system.py
import threading


class MultiAgentSystemManager:
    """
    The MultiAgentSystemManager class is responsible for managing active_threads, their statuses, and processed content.
    It ensures active_threads are properly initialized and maintains their status throughout their lifecycle.

    Attributes:
        active_threads (dict): A dictionary to store thread information indexed by assistant ID.
        processed_content_map (dict): A dictionary to store processed content indexed by (from_assistant_id, to_assistant_id).
        client (OpenAI or AzureOpenAI): The client for interacting with OpenAI or Azure OpenAI services.
        logger (logging.Logger): The logger for logging information and errors.
        thread_manager (ThreadManager): An instance to manage thread creation and status.
        run_manager (RunManager): An instance to manage the lifecycle and status of runs.
        message_manager (MessageManager): An instance to manage user interactions.
        lock (threading.Lock): A threading lock to ensure thread-safe operations on shared resources.
    """

    def __init__(self, client, logger, thread_manager, run_manager, message_manager):
        """
        Initializes the MultiAgentSystemManager with the provided client, logger, thread manager, run manager, and message manager.
        
        Args:
            client (OpenAI or AzureOpenAI): The client for interacting with OpenAI or Azure OpenAI services.
            logger (logging.Logger): The logger for logging information and errors.
            thread_manager (ThreadManager): An instance to manage thread creation and status.
            run_manager (RunManager): An instance to manage the lifecycle and status of runs.
            message_manager (MessageManager): An instance to manage user interactions.
        """
        # Structure: {assistant_id: {'thread_id': str, 'status': str}}
        self.active_threads = {}
        # Structure: {(from_assistant_id, to_assistant_id): [processed_content1, processed_content2, ...]}
        self.processed_content_map = {}
        self.client = client
        self.logger = logger
        self.thread_manager = thread_manager
        self.run_manager = run_manager
        self.message_manager = message_manager
        self.lock = threading.Lock()


    def save_processed_content(self, from_assistant_id, to_assistant_id, processed_content):
        """
        Saves the processed user content using the from_assistant_id and to_assistant_id.

        Args:
            from_assistant_id (str): The assistant identifier from which the content originates.
            to_assistant_id (str): The assistant identifier to which the content is directed.
            processed_content (str): The processed content to store.

        Returns:
            bool: True if content is saved successfully, False otherwise.
        """
        self.logger.info(f"Called save_processed_content with from_assistant_id: {from_assistant_id}, to_assistant_id: {to_assistant_id}")

        # Validate input parameters.
        if not from_assistant_id or not to_assistant_id or not processed_content:
            self.logger.error("from_assistant_id, to_assistant_id, and processed_content cannot be empty.")
            return False

        try:
            # Acquire the lock to ensure thread-safe access to shared resources.
            with self.lock:
                # Create a tuple key from the from_assistant_id and to_assistant_id.
                key = (from_assistant_id, to_assistant_id)
                
                # Check if the key is not already in the processed_content_map.
                if key not in self.processed_content_map:
                    # If the key is not present, initialize an empty list for it.
                    self.processed_content_map[key] = []
                
                # Append the processed content to the list for the key.
                self.processed_content_map[key].append(processed_content)
            
            # Log the storage operation.
            self.logger.info(f"Processed content stored from assistant ID: {from_assistant_id} to assistant ID: {to_assistant_id}.")
            # self.logger.info(f"Stored content: {processed_content}.")
            return True

        except Exception as e:
            # Log any error that occurs during the process.
            self.logger.error(f"Error saving processed content from assistant ID: {from_assistant_id} to assistant ID: {to_assistant_id}: {e}", exc_info=True)
            return False


    def load_processed_content(self, from_assistant_id, to_assistant_id, multiple_retrieval=False):
        """
        Loads the stored processed user content using the from_assistant_id and to_assistant_id.
        Optionally retrieves content from all assistants if multiple_retrieval is True.

        Args:
            from_assistant_id (str): The assistant identifier from which the content originates.
            to_assistant_id (str): The assistant identifier to which the content is directed.
            multiple_retrieval (bool): Whether to retrieve content from all sources, not just the specified to_assistant_id.

        Returns:
            list: A list of stored user content if found, otherwise an empty list.
        """
        self.logger.info(f"Called load_processed_content with from_assistant_id: {from_assistant_id}, to_assistant_id: {to_assistant_id}, multiple_retrieval: {multiple_retrieval}")

        # Validate input parameters.
        if not from_assistant_id or not to_assistant_id:
            self.logger.error("from_assistant_id and to_assistant_id cannot be empty.")
            return []

        try:
            # Acquire the lock to ensure thread-safe access to shared resources.
            with self.lock:
                # Initialize an empty list to hold the retrieved content.
                retrieved_content = []

                if multiple_retrieval:  # Check if multiple_retrieval is set to True.
                    # List to keep track of keys to be removed.
                    keys_to_remove = []
                    
                    # Retrieve content for all from_assistant_id values directed to the specified to_assistant_id.
                    for key in list(self.processed_content_map.keys()):  # Iterate over the keys in processed_content_map.
                        # Check if the key is a valid tuple and matches the to_assistant_id.
                        if isinstance(key, tuple) and len(key) == 2 and key[1] == to_assistant_id:
                            # Extend the retrieved_content list with the content.
                            retrieved_content.extend(self.processed_content_map[key])
                            # Mark the key for removal.
                            keys_to_remove.append(key)
                    
                    # Remove the marked keys.
                    for key in keys_to_remove:
                        del self.processed_content_map[key]  # Delete the key from the dictionary.
                else:
                    # Retrieve content for the specified from_assistant_id and to_assistant_id.
                    key = (from_assistant_id, to_assistant_id)  # Create a tuple key from the from_assistant_id and to_assistant_id.
                    
                    # Check if the key is in processed_content_map.
                    if key in self.processed_content_map:
                        # Remove the key and get its content.
                        retrieved_content = self.processed_content_map.pop(key)

                if not retrieved_content:  # Check if no content was retrieved.
                    self.logger.info(f"No processed content found for from_assistant_id: {from_assistant_id} to assistant ID: {to_assistant_id}.")
                else:
                    # Log the retrieved content.
                    # self.logger.info(f"Retrieved and cleared processed content from assistant ID: {from_assistant_id} to assistant ID: {to_assistant_id}. Content: {retrieved_content}")
                    self.logger.info(f"Retrieved and cleared processed content from assistant ID: {from_assistant_id} to assistant ID: {to_assistant_id}.")
                    
                return retrieved_content

        except Exception as e:
            # Log any error that occurs during the process.
            self.logger.error(f"Error loading processed content from assistant ID: {from_assistant_id} to assistant ID: {to_assistant_id}: {e}", exc_info=True)
            return []


    def check_for_thread_and_status(self, assistant_id):
        """
        Checks if there is an existing thread for the given assistant ID and retrieves its status.

        Args:
            assistant_id (str): The unique identifier for the assistant.

        Returns:
            tuple: A tuple of (thread_id, status) if the thread exists, otherwise (None, None).
        """
        with self.lock:
            if assistant_id in self.active_threads:
                self.logger.debug(f"Found existing thread for assistant ID: {assistant_id}, Thread ID: {self.active_threads[assistant_id]['thread_id']}, Status: {self.active_threads[assistant_id]['status']}.")
                return self.active_threads[assistant_id]['thread_id'], self.active_threads[assistant_id]['status']
            else:
                self.logger.info(f"No thread found for assistant ID: {assistant_id}.")
                return None, None


    def thread_initialization(self, assistant_id):
        """
        Initializes a new thread for the given assistant ID if it does not already exist,
        and sets its status to 'initialized'.

        Args:
            assistant_id (str): The unique identifier for the assistant.

        Returns:
            str: The thread ID of the newly created or existing thread.
        """
        with self.lock:
            if assistant_id not in self.active_threads:
                self.logger.info(f"Attempting to create a new thread for assistant ID: {assistant_id}.")
                thread_id = self.thread_manager.create_thread().id
                if thread_id:
                    self.active_threads[assistant_id] = {
                        'thread_id': thread_id,
                        'status': 'initialized'
                    }
                    self.logger.info(f"New thread {thread_id} created and initialized for assistant ID: {assistant_id}.")
                    return thread_id
                else:
                    self.logger.error(f"Failed to create a new thread for assistant ID: {assistant_id}.")
                    return None
            else:
                thread_id = self.active_threads[assistant_id]['thread_id']
                self.logger.info(f"Thread {thread_id} already exists for assistant ID: {assistant_id}, no new thread created.")
                return thread_id


    def initialize_agent(self, assistant_id):
        """
        Initializes an agent for the given assistant ID. If a thread already exists for the assistant ID,
        it returns a message indicating the existing thread. Otherwise, it creates a new thread and returns
        a message indicating successful initialization.

        Args:
            assistant_id (str): The unique identifier for the assistant.

        Returns:
            str: A message indicating the result of the initialization.
        """
        thread_id, status = self.check_for_thread_and_status(assistant_id)
        if thread_id:
            return f"Found a thread id: '{thread_id}' initialized for assistant id: '{assistant_id}'."
        else:
            thread_id = self.thread_initialization(assistant_id)
            if thread_id:
                self.run_manager.create_and_monitor_run(assistant_id, thread_id)
                self.run_manager.wait_for_run_completion(thread_id)
                return f"Initialization of assistant id: '{assistant_id}' was successful in thread id: '{thread_id}'."
            else:
                self.logger.error(f"Failed to initialize a new thread for assistant ID: {assistant_id}.")
                return f"Failed to initialize a new thread for assistant id: '{assistant_id}'."


    def change_thread_status(self, assistant_id, new_status):
        """
        Updates the status of a thread identified by the assistant ID.

        Args:
            assistant_id (str): The unique identifier for the assistant.
            new_status (str): The new status to set for the thread.
        """
        with self.lock:
            if assistant_id in self.active_threads:
                self.active_threads[assistant_id]['status'] = new_status
                self.logger.info(f"Status of thread {self.active_threads[assistant_id]['thread_id']} updated to {new_status} for assistant ID: {assistant_id}.")
            else:
                self.logger.info(f"Attempted to update status for a non-existent thread with assistant ID: {assistant_id}.")


    def update_assistant_in_thread(self, assistant_id, thread_id):
        """
        Updates the assistant settings in a thread by submitting an update message and creating a run.

        Args:
            assistant_id (str): The unique identifier for the assistant.
            thread_id (str): The thread identifier used for conversation.

        Returns:
            bool: True if the update is successful, False otherwise.
        """
        self.logger.info(f"Updating assistant {assistant_id} in thread {thread_id}.")
        try:
            self.run_manager.wait_for_run_completion(thread_id)
            update_message = f"System message: Initialization. You do not interact directly with users or ask them questions; you solely process the data provided and follow the procedures for data. You will not greet or ask questions, just focus on task processing and delivery."
            self.run_manager.create_and_monitor_run(assistant_id, thread_id, update_message)
            self.logger.info(f"Updated assistant {assistant_id} in thread {thread_id}.")
            self.change_thread_status(assistant_id, 'updated')
            return True
        except Exception as e:
            self.logger.error(f"Error updating assistant in thread: {str(e)}", exc_info=True)
            return False


    def continue_conversation_with_assistant(self, assistant_id, user_content):
        """
        Continues the conversation with an assistant by submitting user content and managing the resulting run.

        Args:
            assistant_id (str): The unique identifier for the assistant.
            user_content (str): The content submitted by the user.

        Returns:
            tuple: A tuple containing a success status, a message detailing the outcome, and the processed content.
        """
        try:
            thread_id, status = self.check_for_thread_and_status(assistant_id)
            if thread_id is None:
                thread_id = self.thread_initialization(assistant_id)

            self.run_manager.wait_for_run_completion(thread_id)
            self.run_manager.create_and_monitor_run(assistant_id, thread_id, user_content)

            return f"Successfuly delivered the user_content."
        except Exception as e:
            self.logger.error(f"Error during conversation continuation: {str(e)}", exc_info=True)
            return f"An error occurred during conversation continuation: {str(e)}"
