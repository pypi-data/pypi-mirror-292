# flexiai/core/utils/helpers.py
import os
import json
import logging
import platform


class HelperFunctions:
    
    @staticmethod
    def clear_console():
        """Clears the console depending on the operating system."""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')


    @staticmethod
    def show_json(obj):
        """
        Print a JSON object or a list of JSON objects.
        """
        if isinstance(obj, list):
            for item in obj:
                print(json.dumps(json.loads(item.model_dump_json()), indent=4))
        else:
            print(json.dumps(json.loads(obj.model_dump_json()), indent=4))


    @staticmethod
    def pretty_print(messages):
        """
        Pretty print a list of message objects. (dict)
        """
        print("=" * 100)
        for msg in messages:
            role = msg['role']
            content_value = msg['content']

            role_name = "User" if role == "user" else "Assistant"
            print(f"{role_name}: {content_value}")
        print("=" * 100)
        print()


    @staticmethod
    def pretty_print_obj(messages):
        """
        Pretty print a list of message objects.
        """
        print("=" * 100)
        for msg in messages:
            role = msg.role
            content_blocks = msg.content
            content_value = " ".join([
                block.text.value for block in content_blocks if hasattr(block, 'text') and hasattr(block.text, 'value')
            ])

            role_name = "User" if role == "user" else "Assistant"
            print(f"{role_name}: {content_value}")
        print("=" * 100)
        print()


    @staticmethod
    def print_run_details(run):
        """
        Print the details of a run object.
        """
        try:
            if hasattr(run, 'dict'):
                print(json.dumps(run.dict(), indent=4))
            else:
                print(json.dumps(run, default=lambda o: o.__dict__, indent=4))
        except TypeError as e:
            logging.error(f"Error serializing object: {e}")
            print(run)


    @staticmethod
    def print_messages_as_json(messages):
        """
        Print messages returned by the retrieve_message_object function in JSON format.

        Args:
            messages (list): List of message objects returned by retrieve_message_object.
        """
        def content_block_to_dict(content_block):
            """
            Convert a TextContentBlock object to a dictionary.
            """
            content_block_dict = content_block.__dict__.copy()
            if hasattr(content_block, 'text') and isinstance(content_block.text, object):
                content_block_dict['text'] = content_block.text.__dict__
            return content_block_dict

        def message_to_dict(message):
            """
            Convert a message object to a dictionary, including nested TextContentBlock objects.
            """
            message_dict = message.__dict__.copy()
            if 'content' in message_dict:
                message_dict['content'] = [content_block_to_dict(content) for content in message_dict['content']]
            return message_dict

        # Convert each message object to a dictionary
        messages_dict = [message_to_dict(message) for message in messages]
        # Print the messages in JSON format
        print(json.dumps(messages_dict, indent=4))


    @staticmethod
    def format_and_track_messages(all_messages, retrieved_messages, USER_ROLE_NAME, ASSISTANT_ROLE_NAME):
        """
        Format and track messages, adding new messages to the message history.

        Args:
            all_messages (list): List to store all message objects.
            retrieved_messages (list): List of new messages retrieved.
            USER_ROLE_NAME (str): Custom name for user role.
            ASSISTANT_ROLE_NAME (str): Custom name for assistant role.

        Returns:
            None
        """
        for msg in retrieved_messages:
            if msg.id not in [m.id for m in all_messages]:
                all_messages.append(msg)

        for msg in all_messages:
            role = ASSISTANT_ROLE_NAME if msg.role == "assistant" else USER_ROLE_NAME
            content_value = " ".join([
                block.text.value for block in msg.content if hasattr(block, 'text') and hasattr(block.text, 'value')
            ]) if msg.content else "No content"
            print(f"{role}: {content_value}")

