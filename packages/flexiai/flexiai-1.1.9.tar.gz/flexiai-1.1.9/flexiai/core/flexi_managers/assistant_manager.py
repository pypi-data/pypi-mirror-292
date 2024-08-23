# flexiai/core/flexi_managers/assistant_manager.py
from openai import NotFoundError, OpenAIError


class AssistantManager:
    """
    AssistantManager is responsible for handling all assistant-related operations, including
    creating, updating, retrieving, deleting assistants, and attaching assistants to threads.

    This manager interacts with the OpenAI Assistants API to manage AI assistants and
    integrate them into ongoing threads. It supports various configuration options to tailor
    the behavior of the assistants.

    Attributes:
        client: An instance of the OpenAI client.
        logger: A logger instance for logging operations and errors.
    """

    def __init__(self, client, logger):
        """
        Initializes the AssistantManager with the necessary client and logger.

        Args:
            client: The OpenAI client to communicate with the API.
            logger: Logger for logging information, warnings, and errors.
        """
        self.client = client
        self.logger = logger


    def create_assistant(
        self, 
        model, 
        instructions, 
        name=None, 
        description=None, 
        tools=None,                 # Default is an empty list, set later if None
        tool_resources=None,        # Default is an empty dictionary, set later if None
        temperature=1.0,            # Default temperature for randomness
        top_p=1.0,                  # Default top-p sampling value
        response_format="auto",     # Default response format
        metadata=None,              # Default metadata set later if None
        **kwargs
    ):
        """
        Creates an AI assistant with the specified settings. This assistant can be customized
        using a variety of parameters like tools, temperature, and more.

        Args:
            model (str): ID of the model to use.
            instructions (str): System instructions that the assistant follows.
            name (str, optional): The name of the assistant.
            description (str, optional): A brief description of the assistant.
            tools (list, optional): A list of tools the assistant can use (e.g., code interpreter, file search).
            tool_resources (dict, optional): Tool-specific resources such as file IDs or vector stores.
            temperature (float, optional): Temperature for controlling randomness. Default is 1.0.
            top_p (float, optional): Top-p sampling value for nucleus sampling. Default is 1.0.
            response_format (str or dict, optional): Format in which the assistant responds. Default is "auto".
            metadata (dict, optional): Metadata associated with the assistant. Default is an empty dictionary.
            **kwargs: Additional optional parameters for customizing the assistant.

        Returns:
            object: The created assistant object.

        Raises:
            OpenAIError: If the API call fails.
            Exception: If an unexpected error occurs during the assistant creation process.
        """
        try:
            assistant_data = {
                "model": model,
                "instructions": instructions,
                "name": name,
                "description": description,
                "tools": tools or [],                       # Empty list if None
                "tool_resources": tool_resources or {},     # Empty dict if None
                "temperature": temperature,
                "top_p": top_p,
                "response_format": response_format,
                "metadata": metadata or {},                 # Empty dict if None
                **kwargs
            }
            response = self.client.beta.assistants.create(**assistant_data)
            self.logger.info(f"Assistant created with ID: {response.id}")
            return response
        except OpenAIError as e:
            self.logger.error(f"Failed to create assistant: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during assistant creation: {str(e)}", exc_info=True)
            raise


    def update_assistant(
        self, 
        assistant_id, 
        model=None, 
        instructions=None, 
        name=None, 
        description=None, 
        tools=None,                 # Default is an empty list, set later if None
        tool_resources=None,        # Default is an empty dictionary, set later if None
        temperature=1.0,            # Default temperature for randomness
        top_p=1.0,                  # Default top-p sampling value
        response_format="auto",     # Default response format
        metadata=None,              # Default metadata set later if None
        **kwargs
    ):
        """
        Updates an existing AI assistant with new parameters or configurations.

        Args:
            assistant_id (str): The ID of the assistant to update.
            model (str, optional): ID of the model to use.
            instructions (str, optional): Updated instructions for the assistant.
            name (str, optional): Updated name of the assistant.
            description (str, optional): Updated description of the assistant.
            tools (list, optional): Updated list of tools for the assistant.
            tool_resources (dict, optional): Updated resources specific to the tools.
            temperature (float, optional): Temperature for controlling randomness. Default is 1.0.
            top_p (float, optional): Top-p sampling value for nucleus sampling. Default is 1.0.
            response_format (str or dict, optional): Updated response format. Default is "auto".
            metadata (dict, optional): Updated metadata associated with the assistant.
            **kwargs: Additional optional parameters for updating the assistant.

        Returns:
            object: The updated assistant object.

        Raises:
            OpenAIError: If the API call fails.
            Exception: If an unexpected error occurs during the assistant update process.
        """
        try:
            # Prepare update data, excluding any None values
            update_data = {
                "model": model,
                "instructions": instructions,
                "name": name,                               # Assistant nane
                "description": description,
                "tools": tools or [],                       # Empty list if None
                "tool_resources": tool_resources or {},     # Empty dict if None
                "temperature": temperature,
                "top_p": top_p,
                "response_format": response_format,
                "metadata": metadata or {},                 # Empty dict if None
                **kwargs
            }

            # Remove any keys with None values
            update_data = {k: v for k, v in update_data.items() if v is not None}

            # Send the update request
            response = self.client.beta.assistants.update(assistant_id, **update_data)
            self.logger.info(f"Assistant updated with ID: {assistant_id}")
            return response
        except OpenAIError as e:
            self.logger.error(f"Failed to update assistant ID {assistant_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during assistant update: {str(e)}", exc_info=True)
            raise


    def retrieve_assistant(self, assistant_id):
        """
        Retrieves the details of a specific assistant by its ID.

        Args:
            assistant_id (str): The ID of the assistant to retrieve.

        Returns:
            dict: The assistant object retrieved.

        Raises:
            OpenAIError: If the API call fails.
            Exception: If an unexpected error occurs during the assistant retrieval process.
        """
        try:
            response = self.client.beta.assistants.retrieve(assistant_id)
            self.logger.info(f"Assistant retrieved: {response}")
            return response
        except OpenAIError as e:
            self.logger.error(f"Failed to retrieve assistant ID {assistant_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during assistant retrieval: {str(e)}", exc_info=True)
            raise


    def delete_assistant(self, assistant_id):
        """
        Deletes a specified assistant by its ID.

        Args:
            assistant_id (str): The ID of the assistant to delete.

        Returns:
            dict: A confirmation object indicating successful deletion.

        Raises:
            OpenAIError: If the API call fails.
            Exception: If an unexpected error occurs during the assistant deletion process.
        """
        try:
            response = self.client.beta.assistants.delete(assistant_id)
            self.logger.info(f"Assistant deleted: {assistant_id}")
            return response
        except OpenAIError as e:
            self.logger.error(f"Failed to delete assistant ID {assistant_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during assistant deletion: {str(e)}", exc_info=True)
            raise


    def attach_assistant_to_thread(self, assistant_id, thread_id):
        """
        Attaches an assistant to an existing thread, allowing the assistant to participate in the thread's conversation.

        Args:
            assistant_id (str): The ID of the assistant to attach.
            thread_id (str): The ID of the thread where the assistant will be attached.

        Returns:
            object: A run object indicating the assistant has been successfully attached to the thread.

        Raises:
            OpenAIError: If the API call to attach the assistant fails.
            Exception: If an unexpected error occurs during the attachment process.
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


    def handle_assistant_for_thread(self, thread_id=None, action="create", assistant_id=None, **kwargs):
        """
        Dynamically handles assistant operations for a thread. It supports creating, updating, retrieving, deleting,
        and attaching an assistant to a specific thread.

        Args:
            thread_id (str, optional): The ID of the thread where the assistant will be attached (for "attach" action).
            action (str): The action to perform. One of "create", "update", "retrieve", "delete", or "attach".
            assistant_id (str, optional): The ID of the assistant to operate on (required for update, retrieve, attach).
            **kwargs: Parameters specific to the assistant operation (e.g., model, instructions, etc.).

        Returns:
            object: The resulting assistant or run object, depending on the action performed.

        Raises:
            ValueError: If an invalid action is specified or required parameters are missing.
            Exception: If an unexpected error occurs during the operation.
        """
        try:
            if action == "create":
                return self.create_assistant(**kwargs)

            elif action == "update" and assistant_id:
                return self.update_assistant(assistant_id, **kwargs)

            elif action == "retrieve" and assistant_id:
                return self.retrieve_assistant(assistant_id)

            elif action == "delete" and assistant_id:
                return self.delete_assistant(assistant_id)

            elif action == "attach" and assistant_id and thread_id:
                return self.attach_assistant_to_thread(assistant_id, thread_id)

            else:
                raise ValueError("Invalid action or missing assistant_id/thread_id for the selected action.")

        except NotFoundError as e:
            self.logger.warning(f"Assistant not found: {e}. This is expected in some scenarios.")
            return None
        except OpenAIError as e:
            self.logger.error(f"OpenAI-specific error: {e}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error handling assistant action {action}: {str(e)}", exc_info=True)
            raise


    def retrieve_assistant_settings(self, assistant_id):
        """
        Retrieves the settings of an assistant, including instructions, model, temperature, top_p, tools, etc.

        Args:
            assistant_id (str): The ID of the assistant to retrieve.

        Returns:
            dict: The assistant's settings including instructions and configuration.
        """
        try:
            # Retrieve the assistant's full settings
            response = self.retrieve_assistant(assistant_id)
            
            # Extract and return relevant settings for evaluation
            settings = {
                "id": response.id,
                "name": response.name,
                "instructions": response.instructions,
                "model": response.model,
                "temperature": response.temperature,
                "top_p": response.top_p,
                "tools": response.tools,
                "tool_resources": response.tool_resources,
                "response_format": response.response_format,
                "metadata": response.metadata
            }

            self.logger.info(f"Assistant settings retrieved for ID: {assistant_id}")
            return settings
        except OpenAIError as e:
            self.logger.error(f"Failed to retrieve assistant settings for ID {assistant_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during assistant settings retrieval: {str(e)}", exc_info=True)
            raise
