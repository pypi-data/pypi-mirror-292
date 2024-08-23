# flexiai/core/flexi_managers/completions_manager.py
from openai import OpenAIError


class CompletionsManager:
    """
    Manages the interactions with the OpenAI API for chat completions, including simple, structured, 
    and function-calling completions. This manager handles the communication, logging, and error handling 
    for these API calls.

    Attributes:
        client (object): The OpenAI client instance for making API requests.
        logger (logging.Logger): Logger instance for recording logs and errors.
    """

    def __init__(self, client, logger):
        """
        Initializes the CompletionsManager with the provided OpenAI client and logger.

        Args:
            client (object): The OpenAI client instance.
            logger (logging.Logger): The logger instance for logging information and errors.
        """
        self.client = client
        self.logger = logger


    def structured_chat_completion(self, model, messages, schema_name, schema):
        """
        Perform a structured chat completion using a specified model and JSON schema.

        This method interacts with the OpenAI API to perform a chat completion where the response is expected
        to follow a structured format defined by a JSON schema. The method logs the process and handles any 
        errors that may occur during the API interaction.

        Args:
            model (str): The OpenAI model to use for the completion.
            messages (list): A list of dictionaries representing the conversation history.
            schema_name (str): The name of the schema defining the response structure.
            schema (dict): The JSON schema that outlines the structure of the expected response.

        Returns:
            dict: The structured output returned by the model if successful.

        Raises:
            OpenAIError: If an error occurs during the interaction with the OpenAI API.
            Exception: If an unexpected error occurs during the process.
        """
        try:
            self.logger.info(f"Performing structured chat completion with model {model}")
            
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": schema
                }
            }
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format=response_format
            )
            
            structured_output = completion.choices[0].message.content
            self.logger.info(f"Received structured output: {structured_output}")
            return structured_output

        except OpenAIError as e:
            self.logger.error(f"An OpenAI error occurred during structured chat completion: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during structured chat completion: {str(e)}", exc_info=True)
            raise


    def simple_chat_completion(self, model, messages):
        """
        Performs a simple chat completion using the provided messages.

        Args:
            model (str): The OpenAI model to use for the completion.
            messages (list): A list of message dictionaries to send to the model.

        Returns:
            str or None: The content of the model's response if successful, None otherwise.

        Raises:
            OpenAIError: If any API-related error occurs during the request.
            Exception: If any unexpected error occurs.
        """
        try:
            self.logger.info(f"Performing simple chat completion with model {model}")
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            message_content = completion.choices[0].message.content
            self.logger.info(f"Received message content: {message_content}")
            return message_content
        except OpenAIError as e:
            self.logger.error(f"An OpenAI error occurred during simple chat completion: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during simple chat completion: {str(e)}", exc_info=True)
            raise


    def handle_refusals(self, completion):
        """
        Handles potential refusals from the model's response.

        Args:
            completion (str or dict): The response from the model, either as a string or a dictionary.

        Returns:
            str or None: The refusal reason if identified, otherwise None.

        Raises:
            Exception: If any unexpected error occurs during refusal handling.
        """
        if isinstance(completion, str):
            self.logger.warning(f"Received string response: {completion}")
            return completion if "can't assist" in completion.lower() else "Potential refusal or error in response"

        try:
            refusal = completion.choices[0].message.get("refusal")
            if refusal:
                self.logger.warning(f"Model refused to respond: {refusal}")
                return refusal
        except Exception as e:
            self.logger.error(f"An error occurred while handling refusal: {str(e)}", exc_info=True)

        return None


    def function_calling_completion(self, model, messages, functions):
        """
        Performs a chat completion with the ability to invoke specified functions.

        Args:
            model (str): The OpenAI model to use for the completion.
            messages (list): A list of message dictionaries to send to the model.
            functions (list): A list of function definitions that the model can call.

        Returns:
            tuple or None: A tuple containing the message content and function call information if successful, None otherwise.

        Raises:
            OpenAIError: If any API-related error occurs during the request.
            Exception: If any unexpected error occurs.
        """
        try:
            self.logger.info(f"Performing function calling completion with model {model}")

            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                functions=functions,
                function_call="auto"
            )

            function_call = completion.choices[0].message.function_call
            message_content = completion.choices[0].message.content

            if function_call:
                self.logger.info(f"Function call made: {function_call}")

            self.logger.info(f"Received message content: {message_content}")
            return message_content, function_call

        except OpenAIError as e:
            self.logger.error(f"An OpenAI error occurred during function calling completion: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during function calling completion: {str(e)}", exc_info=True)
            raise

