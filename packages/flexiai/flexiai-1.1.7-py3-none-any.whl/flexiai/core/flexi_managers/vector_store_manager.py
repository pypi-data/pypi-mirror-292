# flexiai/core/flexi_managers/vector_store_manager.py
import time
from openai import OpenAIError


class VectorStoreManager:
    """
    VectorStoreManager handles the creation of vector stores, uploading files,
    and polling the status of file batches for completion using the OpenAI or Azure OpenAI API.

    Attributes:
        client (OpenAI or AzureOpenAI): The client for interacting with OpenAI or Azure OpenAI services.
        logger (logging.Logger): The logger for logging information and errors.
    """

    def __init__(self, client, logger):
        """
        Initializes the VectorStoreManager instance with the specified client and logger.

        Args:
            client (OpenAI or AzureOpenAI): The client for interacting with OpenAI or Azure OpenAI services.
            logger (logging.Logger): The logger for logging information and errors.
        """
        self.client = client
        self.logger = logger


    def create_vector_store(self, name):
        """
        Creates a new vector store.

        Args:
            name (str): The name of the vector store.

        Returns:
            object: The newly created vector store object.

        Raises:
            OpenAIError: If the API call to create a new vector store fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Creating vector store with name: {name}")
            vector_store = self.client.beta.vector_stores.create(name=name)
            self.logger.info(f"Created vector store with ID: {vector_store.id}")
            return vector_store
        except OpenAIError as e:
            self.logger.error(f"Failed to create vector store: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while creating vector store: {str(e)}", exc_info=True)
            raise RuntimeError(f"Unexpected error: {str(e)}")


    def upload_files_and_poll(self, vector_store_id, file_paths):
        """
        Uploads files to the vector store and polls the status of the file batch for completion.

        Args:
            vector_store_id (str): The ID of the vector store.
            file_paths (list): A list of file paths to upload.

        Returns:
            object: The file batch object after upload and completion.

        Raises:
            OpenAIError: If the API call to upload files or poll status fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Uploading files to vector store ID: {vector_store_id}")
            file_streams = [open(path, "rb") for path in file_paths]
            file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id, files=file_streams
            )

            self.logger.info(f"File batch uploaded with ID: {file_batch.id}")

            # Poll the status of the file batch
            while file_batch.status in ['queued', 'in_progress']:
                self.logger.info(f"File batch status: {file_batch.status}")
                time.sleep(1)
                file_batch = self.client.beta.vector_stores.file_batches.retrieve(
                    vector_store_id=vector_store_id, batch_id=file_batch.id
                )

            if file_batch.status == 'completed':
                self.logger.info(f"File batch {file_batch.id} completed successfully")
                return file_batch
            else:
                self.logger.error(f"File batch {file_batch.id} failed with status: {file_batch.status}")
                raise RuntimeError(f"File batch {file_batch.id} failed with status: {file_batch.status}")
        except OpenAIError as e:
            self.logger.error(f"Failed to upload files to vector store: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while uploading files: {str(e)}", exc_info=True)
            raise RuntimeError(f"Unexpected error: {str(e)}")


    def update_assistant_with_vector_store(self, assistant_id, vector_store_id):
        """
        Updates the assistant to use the new vector store.

        Args:
            assistant_id (str): The ID of the assistant.
            vector_store_id (str): The ID of the vector store.

        Returns:
            object: The updated assistant object.

        Raises:
            OpenAIError: If the API call to update the assistant fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Updating assistant ID: {assistant_id} with vector store ID: {vector_store_id}")
            assistant = self.client.beta.assistants.update(
                assistant_id=assistant_id,
                tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
            )
            self.logger.info(f"Assistant ID: {assistant.id} updated with vector store ID: {vector_store_id}")
            return assistant
        except OpenAIError as e:
            self.logger.error(f"Failed to update assistant: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while updating assistant: {str(e)}", exc_info=True)
            raise RuntimeError(f"Unexpected error: {str(e)}")


    def list_vector_stores(self):
        """
        Retrieves a list of all existing vector stores.

        Returns:
            list: A list of vector store objects.

        Raises:
            OpenAIError: If the API call to list vector stores fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info("Listing all vector stores")
            vector_stores = self.client.beta.vector_stores.list()
            
            vector_store_list = [vs for vs in vector_stores]
            self.logger.info(f"Retrieved {len(vector_store_list)} vector stores")
            
            return vector_store_list
        except OpenAIError as e:
            self.logger.error(f"Failed to list vector stores: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while listing vector stores: {str(e)}", exc_info=True)
            raise RuntimeError(f"Unexpected error: {str(e)}")


    def retrieve_vector_store_details(self, vector_store_id):
        """
        Retrieves detailed information about a specific vector store.

        Args:
            vector_store_id (str): The ID of the vector store.

        Returns:
            object: The vector store object with detailed information.

        Raises:
            OpenAIError: If the API call to retrieve vector store details fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Retrieving details for vector store ID: {vector_store_id}")
            vector_store = self.client.beta.vector_stores.retrieve(vector_store_id=vector_store_id)
            self.logger.info(f"Retrieved details for vector store ID: {vector_store.id}")
            return vector_store
        except OpenAIError as e:
            self.logger.error(f"Failed to retrieve vector store details: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while retrieving vector store details: {str(e)}", exc_info=True)
            raise RuntimeError(f"Unexpected error: {str(e)}")


    def delete_vector_store(self, vector_store_id):
        """
        Deletes a vector store.

        Args:
            vector_store_id (str): The ID of the vector store.

        Returns:
            bool: True if the vector store was deleted successfully, False otherwise.

        Raises:
            OpenAIError: If the API call to delete the vector store fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Deleting vector store ID: {vector_store_id}")
            self.client.beta.vector_stores.delete(vector_store_id=vector_store_id)
            self.logger.info(f"Deleted vector store ID: {vector_store_id}")
            return True
        except OpenAIError as e:
            self.logger.error(f"Failed to delete vector store: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while deleting vector store: {str(e)}", exc_info=True)
            raise RuntimeError(f"Unexpected error: {str(e)}")


    def list_files_in_vector_store(self, vector_store_id, batch_id):
        """
        Lists all files that have been uploaded to a specific vector store in Azure OpenAI.

        Args:
            vector_store_id (str): The ID of the vector store.
            batch_id (str): The ID of the file batch.

        Returns:
            list: A list of files in the vector store.

        Raises:
            OpenAIError: If the API call to list files in the vector store fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Listing files in vector store ID: {vector_store_id} for batch ID: {batch_id}")
            
            # Use the correct method to list files with both vector_store_id and batch_id
            files = self.client.beta.vector_stores.file_batches.list_files(vector_store_id=vector_store_id, batch_id=batch_id)
            
            file_list = [file for file in files]
            self.logger.info(f"Retrieved {len(file_list)} files from vector store ID: {vector_store_id} for batch ID: {batch_id}")
            
            return file_list
        except OpenAIError as e:
            self.logger.error(f"Failed to list files in vector store: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while listing files: {str(e)}", exc_info=True)
            raise RuntimeError(f"Unexpected error: {str(e)}")


    def retrieve_file_batch_details(self, vector_store_id, batch_id):
        """
        Retrieves the status and details of a specific file batch within a vector store.

        Args:
            vector_store_id (str): The ID of the vector store.
            batch_id (str): The ID of the file batch.

        Returns:
            object: The file batch object with detailed information.

        Raises:
            OpenAIError: If the API call to retrieve file batch details fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Retrieving details for file batch ID: {batch_id} in vector store ID: {vector_store_id}")
            file_batch = self.client.beta.vector_stores.file_batches.retrieve(
                vector_store_id=vector_store_id, batch_id=batch_id
            )
            self.logger.info(f"Retrieved details for file batch ID: {file_batch.id}")
            return file_batch
        except OpenAIError as e:
            self.logger.error(f"Failed to retrieve file batch details: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while retrieving file batch details: {str(e)}", exc_info=True)
            raise RuntimeError(f"Unexpected error: {str(e)}")


    def search_files_in_vector_store(self, vector_store_id, query):
        """
        Searches for files in a vector store based on a query.

        Args:
            vector_store_id (str): The ID of the vector store.
            query (str): The search query.

        Returns:
            list: A list of search results.

        Raises:
            OpenAIError: If the API call to search files fails.
            Exception: If an unexpected error occurs.
        """
        try:
            self.logger.info(f"Searching files in vector store ID: {vector_store_id} with query: {query}")
            files = self.client.beta.vector_stores.files.list(vector_store_id=vector_store_id)
            
            # Adjust the filtering criteria based on available attributes
            search_results = [file for file in files if query in file.id or query in file.status]
            
            self.logger.info(f"Retrieved {len(search_results)} search results from vector store ID: {vector_store_id}")
            return search_results
        except OpenAIError as e:
            self.logger.error(f"Failed to search files in vector store: {str(e)}", exc_info=True)
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except AttributeError as e:
            self.logger.error(f"Failed to search files in vector store due to missing method: {str(e)}", exc_info=True)
            raise RuntimeError(f"Attribute error: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while searching files: {str(e)}", exc_info=True)
            raise RuntimeError(f"Unexpected error: {str(e)}")
