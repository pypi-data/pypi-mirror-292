# flexiai/core/flexi_managers/message_manager.py
from openai import OpenAIError


class MessageManager:
    
    def __init__(self, client, logger):
        """
        Initializes the MessageManager class.

        Args:
            client (object): The OpenAI client instance.
            logger (object): The logger instance.
        """
        self.client = client
        self.logger = logger


    def add_user_message(self, thread_id, user_message):
        """
        Adds a user message to a specified thread.

        Args:
            thread_id (str): The ID of the thread.
            user_message (str): The user's message content.

        Returns:
            object: The message object that was added to the thread.

        Raises:
            OpenAIError: If the API call to add a user message fails.
            Exception: If an unexpected error occurs.
        """
        try:
            # self.logger.info(f"Adding user message to thread {thread_id}: {user_message}")
            message = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )
            self.logger.info(f"Added user message with ID: {message.id}")
            return message
        except OpenAIError as e:
            self.logger.error(f"Failed to add a user message to the thread {thread_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while adding a user message to thread {thread_id}: {str(e)}", exc_info=True)
            raise


    def retrieve_messages(self, thread_id, order='desc', limit=20):
        """
        Retrieves messages from a specified thread.

        Args:
            thread_id (str): The ID of the thread.
            order (str, optional): The order in which to retrieve messages, either 'asc' or 'desc'. Defaults to 'desc'.
            limit (int, optional): The number of messages to retrieve. Defaults to 20.

        Returns:
            list: A list of dictionaries containing the message ID, role, and content of each message.

        Raises:
            OpenAIError: If the API call to retrieve messages fails.
            Exception: If an unexpected error occurs.
        """
        try:
            params = {'order': order, 'limit': limit}
            response = self.client.beta.threads.messages.list(thread_id=thread_id, **params)
            if not response.data:
                self.logger.info("No data found in the response or no messages.")
                return []

            self.logger.info(f"Retrieved {len(response.data)} messages from thread {thread_id}")
            messages = response.data[::-1]
            formatted_messages = []

            for message in messages:
                message_id = message.id
                role = message.role
                content_blocks = message.content
                content_value = " ".join([
                    block.text.value for block in content_blocks if hasattr(block, 'text') and hasattr(block.text, 'value')
                ])

                # self.logger.info(f"Message ID: {message_id}, Role: {role}, Content: {content_blocks}")

                formatted_messages.append({
                    'message_id': message_id,
                    'role': role,
                    'content': content_value
                })

            return formatted_messages
        except OpenAIError as e:
            self.logger.error(f"Failed to fetch messages for thread {thread_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while fetching messages for thread {thread_id}: {str(e)}", exc_info=True)
            raise


    def retrieve_message_object(self, thread_id, order='asc', limit=20):
        """
        Retrieves message objects from a specified thread.

        Args:
            thread_id (str): The ID of the thread.
            order (str, optional): The order in which to retrieve messages, either 'asc' or 'desc'. Defaults to 'asc'.
            limit (int, optional): The number of messages to retrieve. Defaults to 20.

        Returns:
            list: A list of message objects.

        Raises:
            OpenAIError: If the API call to retrieve messages fails.
            Exception: If an unexpected error occurs.
        """
        try:
            params = {'order': order, 'limit': limit}
            response = self.client.beta.threads.messages.list(thread_id=thread_id, **params)
            if not response.data:
                self.logger.info("No data found in the response or no messages.")
                return []

            # self.logger.info(f"Retrieved {len(response.data)} messages from thread {thread_id}")
            messages = response.data
            return messages
        except OpenAIError as e:
            self.logger.error(f"Failed to fetch messages for thread {thread_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while fetching messages for thread {thread_id}: {str(e)}", exc_info=True)
            raise


    def process_and_print_messages(self, messages):
        """
        Processes and prints the role and content of each message.

        Args:
            messages (list): The list of message objects.
        """
        for message in messages:
            role = "Assistant" if message.role == "assistant" else "User"
            content_blocks = message.content
            content_value = " ".join([
                block.text.value for block in content_blocks if hasattr(block, 'text') and hasattr(block.text, 'value')
            ])

            print(f"{role}: {content_value}")


    def add_messages_dynamically(self, thread_id, messages, role=None, metadata=None):
        """
        Adds multiple messages to a specified thread dynamically with optional metadata.

        Args:
            thread_id (str): The ID of the thread.
            messages (list): A list of dictionaries where each dictionary contains:
                - content (str): The content of the message.
                - metadata (dict, optional): Metadata to include with the message.
            role (str, optional): The role of the message sender. Defaults to None.
            metadata (dict, optional): Metadata to include with each message if not provided in individual messages.

        Returns:
            list: A list of message objects that were added to the thread.

        Raises:
            OpenAIError: If the API call to add a message fails.
            Exception: If an unexpected error occurs.
        """
        added_messages = []
        for message in messages:
            content = message.get('content')
            message_metadata = message.get('metadata', metadata or {})
            try:
                # self.logger.info(f"Adding message to thread {thread_id}: {content}")
                message_obj = self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role=role if role else 'user',  # Use 'user' as default role if not specified
                    content=content,
                    metadata=message_metadata
                )
                self.logger.info(f"Added message with ID: {message_obj.id}")
                added_messages.append(message_obj)
            except OpenAIError as e:
                self.logger.error(f"Failed to add message to thread {thread_id}: {str(e)}", exc_info=True)
                raise
            except Exception as e:
                self.logger.error(f"An unexpected error occurred while adding message to thread {thread_id}: {str(e)}", exc_info=True)
                raise
        return added_messages


    def retrieve_messages_dynamically(self, thread_id, order='asc', limit=20, retrieve_all=False, last_retrieved_id=None):
        """
        Retrieves messages from a specified thread dynamically.

        Args:
            thread_id (str): The ID of the thread from which to retrieve messages.
            order (str, optional): The order in which to retrieve messages, either 'asc' or 'desc'. Defaults to 'asc'.
            limit (int, optional): The maximum number of messages to retrieve in a single request. Defaults to 20.
            retrieve_all (bool, optional): Whether to retrieve all messages in the thread. If False, only retrieves up to the limit. Defaults to False.
            last_retrieved_id (str, optional): The ID of the last retrieved message to fetch messages after it. Defaults to None.

        Returns:
            list: A list of message objects retrieved from the thread.

        Raises:
            OpenAIError: If the API call to retrieve messages fails.
            Exception: If an unexpected error occurs.
        """
        all_messages = []
        params = {'order': order, 'limit': limit}
        if last_retrieved_id:
            params['after'] = last_retrieved_id
        has_more = True

        while has_more:
            try:
                response = self.client.beta.threads.messages.list(thread_id=thread_id, **params)
                if not response.data:
                    self.logger.info("No data found in the response or no messages.")
                    return []

                # self.logger.info(f"Retrieved {len(response.data)} messages from thread {thread_id}")
                messages = response.data
                all_messages.extend(messages)

                if not retrieve_all or not response.has_more:
                    break

                # Update the params to get the next set of messages
                params['after'] = response.last_id
                has_more = response.has_more

            except OpenAIError as e:
                self.logger.error(f"Failed to fetch messages for thread {thread_id}: {str(e)}", exc_info=True)
                raise
            except Exception as e:
                self.logger.error(f"An unexpected error occurred while fetching messages for thread {thread_id}: {str(e)}", exc_info=True)
                raise

        return all_messages
