# flexiai/assistant/functions_registry.py
import logging
import os
import importlib.util
import asyncio
from flexiai.assistant.functions_manager import FunctionsManager
from flexiai.config.config import config

logger = logging.getLogger(__name__)


class FunctionRegistry:
    """
    Handles the registration of core and user functions in the FlexiAI framework.
    """

    def __init__(self, multi_agent_system, run_manager):
        """
        Initializes the FunctionRegistry with the necessary dependencies.
        """
        self.multi_agent_system = multi_agent_system
        self.run_manager = run_manager
        self.core_personal_functions = {}
        self.core_assistant_functions = {}
        self.user_personal_functions = {}
        self.user_assistant_functions = {}


    async def initialize_registry(self):
        """
        Initializes the function registry by mapping core and user-defined functions.
        """
        await self.map_core_functions()
        await self.map_user_functions()

        # Inject function mappings into RunManager
        self.run_manager.update_function_mappings(
            self.get_combined_personal_functions(),
            self.get_combined_assistant_functions()
        )


    async def map_core_functions(self):
        """
        Maps the core functions provided by the FlexiAI framework.
        """
        logger.info("Mapping core functions...")

        functions_manager = FunctionsManager(self.multi_agent_system, self.run_manager)
        self.core_personal_functions = {
            'save_processed_content': functions_manager.save_processed_content,
            'load_processed_content': functions_manager.load_processed_content,
            'initialize_agent': functions_manager.initialize_agent,
        }
        self.core_assistant_functions = {
            'communicate_with_assistant': functions_manager.continue_conversation_with_assistant,
        }

        logger.info(f"FR core personal functions: {list(self.core_personal_functions.keys())}")
        logger.info(f"FR core assistant functions: {list(self.core_assistant_functions.keys())}")


    async def map_user_functions(self):
        """
        Dynamically loads and registers user-defined functions by merging them with the core functions.
        """
        logger.info("Mapping user-defined functions...")

        user_project_root_dir = config.USER_PROJECT_ROOT_DIR
        user_function_mapping_path = os.path.join(user_project_root_dir, 'user_flexiai_rag', 'user_functions_mapping.py')

        if os.path.exists(user_function_mapping_path):
            try:
                spec = importlib.util.spec_from_file_location('user_functions_mapping', user_function_mapping_path)
                user_function_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(user_function_module)

                # Call the map_user_functions function without any parameters
                user_personal_functions, user_assistant_functions = await user_function_module.map_user_functions()

                self.user_personal_functions.update(user_personal_functions)
                self.user_assistant_functions.update(user_assistant_functions)

                logger.info(f"FR user personal functions: {list(self.user_personal_functions.keys())}")
                logger.info(f"FR user assistant functions: {list(self.user_assistant_functions.keys())}")

            except Exception as e:
                logger.error(f"Failed to load user functions: {e}", exc_info=True)
                raise e
        else:
            logger.warning(f"user_functions_mapping.py not found at {user_function_mapping_path}")


    def get_combined_personal_functions(self):
        """
        Returns a dictionary containing both core and user-defined personal functions.
        """
        return {**self.core_personal_functions, **self.user_personal_functions}


    def get_combined_assistant_functions(self):
        """
        Returns a dictionary containing both core and user-defined assistant functions.
        """
        return {**self.core_assistant_functions, **self.user_assistant_functions}
