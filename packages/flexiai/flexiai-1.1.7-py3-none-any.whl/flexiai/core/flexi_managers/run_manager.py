# flexiai/core/flexi_managers/run_manager.py
import asyncio
import time
import json
import nest_asyncio
from openai import OpenAIError

class RunManager:
    def __init__(self, client, logger, message_manager, function_registry):
        """
        Initializes the RunManager.
        """
        self.client = client
        self.logger = logger
        self.message_manager = message_manager
        self.personal_function_mapping = {}
        self.assistant_function_mapping = {}

        # RunManager will not initialize the function_registry immediately. It will be done after initialization.
        self.logger.info("RunManager initialized.")


    def initialize_function_registry(self):
        """
        Initialize the function registry, loading core and user functions.
        """
        asyncio.run(self.function_registry.initialize_registry())
        self.logger.info("RunManager initialized with function mappings.")


    def update_function_mappings(self, personal_function_mapping, assistant_function_mapping):
        """
        Updates the function mappings for personal and assistant functions.
        """
        self.personal_function_mapping = personal_function_mapping
        self.assistant_function_mapping = assistant_function_mapping
        self.logger.info(f"RunManager updated with personal functions: {list(personal_function_mapping.keys())}")
        self.logger.info(f"RunManager updated with assistant functions: {list(assistant_function_mapping.keys())}")


    def create_and_monitor_run(self, assistant_id, thread_id, user_message=None, role=None, metadata=None):
        """
        Creates and runs a thread with the specified assistant, optionally adding a user message,
        and monitors its status until completion or failure.

        Args:
            assistant_id (str): The ID of the assistant.
            thread_id (str): The ID of the thread.
            user_message (str, optional): The user's message content to add before creating the run.
            role (str, optional): The role of the message sender. Defaults to 'user'.
            metadata (dict, optional): Metadata to include with the message.

        Returns:
            None

        Raises:
            OpenAIError: If any API call within this function fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Starting a new run for thread {thread_id} with assistant {assistant_id}")

            # Wait for any active run to complete
            self.wait_for_run_completion(thread_id)

            # Add the user's message to the thread if provided
            if user_message:
                messages_to_add = [{"content": user_message, "metadata": metadata}]
                self.message_manager.add_messages_dynamically(thread_id, messages_to_add, role)

            # Create the run
            run = self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

            # Monitor the status of the run
            while run.status in ['queued', 'in_progress', 'cancelling', 'requires_action']:
                self.logger.info(f"Run status: {run.status}")
                if run.status == 'requires_action':
                    self.handle_requires_action(run, assistant_id, thread_id)
                time.sleep(1)  # Wait for 1 second before checking again
                run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

            # Check the final status of the run
            if run.status == 'completed':
                self.logger.info(f"Run {run.id} completed successfully for thread {thread_id}")
            else:
                self.logger.error(f"Run {run.id} failed with status: {run.status}")

        except OpenAIError as e:
            self.logger.error(f"Failed to run thread ID {thread_id} with assistant ID {assistant_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while running thread ID {thread_id} with assistant ID {assistant_id}: {str(e)}", exc_info=True)
            raise


    def create_run(self, assistant_id, thread_id):
        """
        Creates and runs a thread with the specified assistant, monitoring its status
        until completion or failure.

        Args:
            assistant_id (str): The ID of the assistant.
            thread_id (str): The ID of the thread.

        Returns:
            object: The run object if successful, None otherwise.

        Raises:
            OpenAIError: If any API call within this function fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Starting a new run for thread {thread_id} with assistant {assistant_id}")
            
            # Wait for any active run to complete
            self.wait_for_run_completion(thread_id)
            
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id, assistant_id=assistant_id
            )

            # Monitor the status of the run
            while run.status in ['queued', 'in_progress', 'cancelling', 'requires_action']:
                self.logger.info(f"Run status: {run.status}")
                if run.status == 'requires_action':
                    self.handle_requires_action(run, assistant_id, thread_id)
                time.sleep(1)  # Wait for 1 second before checking again
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id, run_id=run.id
                )

            # Check the final status of the run
            if run.status == 'completed':
                self.logger.info(f"Run {run.id} completed successfully for thread {thread_id}")
                return run
            else:
                self.logger.error(f"Run {run.id} failed with status: {run.status}")
                return None
        except OpenAIError as e:
            self.logger.error(f"An error occurred during thread run for thread {thread_id} with assistant {assistant_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during thread run for thread {thread_id} with assistant {assistant_id}: {str(e)}", exc_info=True)
            raise
        
    def create_advanced_run(self, assistant_id, thread_id, user_message):
        """
        Creates and runs a thread with the specified assistant and user message, 
        monitoring its status until completion or failure.

        Args:
            assistant_id (str): The ID of the assistant.
            thread_id (str): The ID of the thread.
            user_message (str): The user's message content.

        Returns:
            object: The run object if successful, None otherwise.

        Raises:
            OpenAIError: If any API call within this function fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Starting a new run for thread {thread_id} with assistant {assistant_id}")
            
            # Wait for any active run to complete
            self.wait_for_run_completion(thread_id)
            
            # Add the user's message to the thread
            self.message_manager.add_user_message(thread_id, user_message)
            
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id, assistant_id=assistant_id
            )

            # Monitor the status of the run
            while run.status in ['queued', 'in_progress', 'cancelling', 'requires_action']:
                self.logger.info(f"Run status: {run.status}")
                if run.status == 'requires_action':
                    self.handle_requires_action(run, assistant_id, thread_id)
                time.sleep(1)  # Wait for 1 second before checking again
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id, run_id=run.id
                )

            # Check the final status of the run
            if run.status == 'completed':
                self.logger.info(f"Run {run.id} completed successfully for thread {thread_id}")
            else:
                self.logger.error(f"Run {run.id} failed with status: {run.status}")

            return run
        except OpenAIError as e:
            self.logger.error(f"An error occurred during thread run for thread {thread_id} with assistant {assistant_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during thread run for thread {thread_id} with assistant {assistant_id}: {str(e)}", exc_info=True)
            raise


    def wait_for_run_completion(self, thread_id):
        """
        Waits for any active runs in the thread to complete.

        Args:
            thread_id (str): The ID of the thread.

        Raises:
            OpenAIError: If an error occurs when interacting with the OpenAI API.
            Exception: If an unexpected error occurs during the process.
        """
        try:
            while True:
                self.logger.info(f"Checking for active runs in thread {thread_id}")
                runs = self.client.beta.threads.runs.list(thread_id=thread_id)
                active_runs = [run for run in runs.data if run.status in ["queued", "in_progress", "cancelling"]]
                if active_runs:
                    self.logger.info(f"Run {active_runs[0].id} is currently {active_runs[0].status}. Waiting for completion...")
                    time.sleep(1)  # Wait for 1 second before checking again
                else:
                    self.logger.info(f"No active run in thread {thread_id}. Proceeding...")
                    break
        except OpenAIError as e:
            self.logger.error(f"Failed to retrieve thread runs for thread {thread_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while waiting for run completion in thread {thread_id}: {str(e)}", exc_info=True)
            raise
            

    def handle_requires_action(self, run, assistant_id, thread_id):
        """
        Handles the required actions for a given run by executing the necessary tool functions either in parallel or sequentially.

        Args:
            run (Run): The run object containing the required action.
            assistant_id (str): The ID of the assistant handling the action.
            thread_id (str): The ID of the thread in which the action is being handled.

        Raises:
            OpenAIError: If there is an error interacting with the OpenAI API.
            Exception: For any general exceptions that occur during the processing of tool outputs.
        """
        self.logger.info(f"Handling required action for run ID: {run.id} with assistant ID: {assistant_id}.")

        # Automatically determine whether to use parallel processing
        use_parallel = len(run.required_action.submit_tool_outputs.tool_calls) > 2

        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tasks = []

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                self.logger.info(f"Function Name: {function_name}, Arguments: {arguments}")

                tasks.append({
                    'function_name': function_name,
                    'parameters': arguments
                })

            tool_outputs = []
            if use_parallel:
                try:
                    results = self.call_parallel_functions(tasks)

                    for tool_call, result in zip(tool_calls, results):
                        if isinstance(result, Exception):
                            tool_output = {
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"status": False, "message": str(result), "result": None})
                            }
                        else:
                            tool_output = {
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"status": True, "message": "Success", "result": result})
                            }

                        tool_outputs.append(tool_output)
                except OpenAIError as e:
                    self.logger.error(f"OpenAI API error when submitting tool outputs for run ID {run.id} in thread {thread_id} with assistant {assistant_id}: {str(e)}", exc_info=True)
                    raise
                except Exception as e:
                    self.logger.error(f"General error when submitting tool outputs for run ID {run.id} in thread {thread_id} with assistant {assistant_id}: {str(e)}", exc_info=True)
                    raise
            else:
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    self.logger.info(f">>> Function Name: '{function_name}' >>> Arguments: {arguments}")

                    action_type = self.determine_action_type(function_name)

                    try:
                        if action_type == "call_assistant":
                            self.logger.info(f"Calling another assistant with arguments: {arguments}")
                            result = self.call_assistant_with_arguments(function_name, **arguments)
                        else:
                            self.logger.info(f"Executing personal function with arguments: {arguments}")
                            result = self.execute_personal_function_with_arguments(function_name, **arguments)

                        tool_output = {
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"status": True, "message": "Success", "result": result})
                        }
                    except Exception as e:
                        tool_output = {
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"status": False, "message": str(e), "result": None})
                        }
                        self.logger.error(f"Error executing tool call {tool_call.id}: {str(e)}", exc_info=True)

                    tool_outputs.append(tool_output)

            try:
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                self.logger.info(f"Successfully submitted tool outputs for run ID: {run.id}")
            except OpenAIError as e:
                self.logger.error(f"OpenAI API error when submitting tool outputs for run ID {run.id} in thread {thread_id} with assistant {assistant_id}: {str(e)}", exc_info=True)
                raise
            except Exception as e:
                self.logger.error(f"General error when submitting tool outputs for run ID {run.id} in thread {thread_id} with assistant {assistant_id}: {str(e)}", exc_info=True)
                raise
        else:
            self.logger.info(f"No required action for this run ID: {run.id}")


    def determine_action_type(self, function_name):
        """
        Determines the action type for a given function name.

        Args:
            function_name (str): The name of the function.

        Returns:
            str: The action type, either "call_assistant" or "personal_function".
        """
        self.logger.info(f"Determining action type for function: {function_name}")
        if function_name.endswith("_assistant"):
            action_type = "call_assistant"
        else:
            action_type = "personal_function"
        self.logger.info(f"Action type for function {function_name}: {action_type}")
        return action_type


    def execute_personal_function_with_arguments(self, function_name, **arguments):
        """
        Executes a personal function with given arguments.

        Args:
            function_name (str): The name of the personal function.
            arguments (dict): A dictionary of arguments to pass to the function.

        Returns:
            object: The result of the function execution.
        """
        self.logger.info(f"Attempting to execute function: {function_name} with arguments: {arguments}")
        func = self.personal_function_mapping.get(function_name, None)
        if callable(func):
            try:
                result = func(**arguments)
                self.logger.info(f"Personal Function {function_name} executed.")
                return result
            except Exception as e:
                self.logger.error(f"Error executing {function_name}: {str(e)}", exc_info=True)
                raise e
        else:
            self.logger.warning(f"Function {function_name} not found in mapping.")
            raise ValueError(f"Function not found: {function_name}")


    def call_assistant_with_arguments(self, function_name, **arguments):
        """
        Calls an assistant function with given arguments.

        Args:
            function_name (str): The name of the assistant function.
            arguments (dict): A dictionary of arguments to pass to the function.

        Returns:
            object: The result of the function execution.

        Raises:
            ValueError: If the function is not defined.
        """
        self.logger.info(f"Attempting to dispatch an assistant using the function: {function_name} with arguments: {arguments}")
        func = self.assistant_function_mapping.get(function_name, None)
        if callable(func):
            try:
                result = func(**arguments)
                # self.logger.info(f"Call Assistant Function {function_name} executed.")
                return result
            except Exception as e:
                self.logger.error(f"Error executing {function_name}: {str(e)}", exc_info=True)
                raise e
        else:
            error_message = f"Function {function_name} is not defined."
            self.logger.error(error_message)
            raise ValueError(error_message)


    async def parallel_tool_calls(self, tasks):
        """
        Executes tool calls in parallel.

        Args:
            tasks (list): A list of task dictionaries containing function names and parameters.

        Returns:
            list: A list of results from the parallel execution of tool calls.

        Raises:
            Exception: If an unexpected error occurs during the parallel execution.
        """
        
        async def call_function(task):
            try:
                self.logger.info(f"==== Starting Parallel Tool Call ====")
                self.logger.info(f"Calling function {task['function_name']} with parameters: {task['parameters']}")
                response = await self.execute_task(task['function_name'], task['parameters'])
                self.logger.info(f"Function {task['function_name']} completed with response: {response}")
                return response
            except OpenAIError as e:
                self.logger.error(f"Error calling function {task['function_name']}: {str(e)}", exc_info=True)
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error calling function {task['function_name']}: {str(e)}", exc_info=True)
                raise

        results = await asyncio.gather(*(call_function(task) for task in tasks), return_exceptions=True)
        return results


    async def execute_task(self, function_name, parameters):
        """
        Executes a task for a given function name and parameters.

        Args:
            function_name (str): The name of the function to execute.
            parameters (dict): The parameters to pass to the function.

        Returns:
            object: The result of the function execution.

        Raises:
            ValueError: If the function is not found or not callable.
            Exception: If an error occurs during the function execution.
        """
        self.logger.info(f"Executing task for function: {function_name} with parameters: {parameters}")
        if function_name in self.personal_function_mapping:
            func = self.personal_function_mapping[function_name]
        elif function_name in self.assistant_function_mapping:
            func = self.assistant_function_mapping[function_name]
        else:
            error_message = f"Function {function_name} not found in mapping."
            self.logger.error(error_message)
            raise ValueError(error_message)

        if callable(func):
            try:
                result = await func(**parameters) if asyncio.iscoroutinefunction(func) else func(**parameters)
                self.logger.info(f"Task {function_name} executed successfully.")
                return result
            except Exception as e:
                error_message = f"Error executing task {function_name}: {str(e)}"
                self.logger.error(error_message, exc_info=True)
                raise
        else:
            error_message = f"Function {function_name} is not callable."
            self.logger.error(error_message)
            raise ValueError(error_message)


    def call_parallel_functions(self, tasks):
        """
        Calls functions in parallel using asyncio.

        Args:
            tasks (list): A list of task dictionaries containing function names and parameters.

        Returns:
            list: A list of results from the parallel execution of functions.

        Raises:
            Exception: If an unexpected error occurs during the parallel execution.
        """
        try:
            nest_asyncio.apply()
            return asyncio.run(self.parallel_tool_calls(tasks))
        except Exception as e:
            self.logger.error(f"An error occurred during parallel function execution: {str(e)}", exc_info=True)
            raise

        
    def assistant_transformer(self, thread_id, new_assistant_id):
        """
        Attaches a new assistant to an existing thread and runs the thread to speak with the new assistant.

        Args:
            thread_id (str): The ID of the existing thread.
            new_assistant_id (str): The ID of the new assistant to attach.

        Returns:
            object: The final run object indicating the result of the interaction.

        Raises:
            OpenAIError: If any API call fails.
            Exception: If an unexpected error occurs.
        """
        try:
            # Attach the new assistant to the thread
            self.logger.info(f"Attaching new assistant ID: {new_assistant_id} to thread ID: {thread_id}")
            run = self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=new_assistant_id)
            self.logger.info(f"Attached new assistant ID: {new_assistant_id} to thread ID: {thread_id}")

            # Poll the status of the run
            while True:
                run_status = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                status = run_status.status
                self.logger.info(f"Current status of run {run.id} for thread {thread_id}: {status}")

                if status == "requires_action":
                    self.handle_requires_action(run, new_assistant_id, thread_id)
                elif status in ["completed", "failed", "cancelled"]:
                    self.logger.info(f"Final status of run {run.id} for thread {thread_id}: {status}")
                    return run_status
                elif status in ["queued", "in_progress", "cancelling"]:
                    self.logger.info(f"Run {run.id} is in progress. Current status: {status}")
                else:
                    self.logger.warning(f"Encountered an unknown status for run {run.id}: {status}")

                time.sleep(1)  # Wait for 1 second before checking again

        except OpenAIError as e:
            self.logger.error(f"Failed to run thread ID {thread_id} with new assistant ID {new_assistant_id}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while running thread ID {thread_id} with new assistant ID {new_assistant_id}: {str(e)}", exc_info=True)
            raise
