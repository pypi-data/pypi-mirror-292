# flexiai/core/flexi_managers/embedding_manager.py
import numpy as np
import faiss
from openai import OpenAIError


class EmbeddingManager:
    """
    EmbeddingManager handles the creation of embeddings using OpenAI's API.

    Attributes:
        client (OpenAI or AzureOpenAI): The client for interacting with OpenAI or Azure OpenAI services.
        logger (logging.Logger): The logger for logging information and errors.
    """

    def __init__(self, client, logger):
        """
        Initializes the EmbeddingManager with the OpenAI client and logger.

        Args:
            client (object): The OpenAI client instance.
            logger (logging.Logger): The logger instance for logging information.
        """
        self.client = client
        self.logger = logger


    def create_embeddings(self, text, model="text-embedding-ada-002", chunk_size=1000):
        """
        Creates embeddings for the given text using OpenAI's embedding model.
        Text is split into chunks if it exceeds the chunk size.

        Args:
            text (str): The text to create embeddings for.
            model (str): The model to use for creating embeddings. Default is "text-embedding-ada-002".
            chunk_size (int): The maximum number of tokens in each chunk.

        Returns:
            np.ndarray: Concatenated embeddings for the text chunks.
        """
        try:
            # Clean and validate text
            if not isinstance(text, str) or len(text.strip()) == 0:
                self.logger.error(f"Invalid text input for embedding: {text}")
                return None

            # Split text into chunks
            tokens = text.split()
            chunks = [' '.join(tokens[i:i + chunk_size]) for i in range(0, len(tokens), chunk_size)]
            self.logger.info(f"Text split into {len(chunks)} chunks for embedding.")

            embeddings = []
            for chunk in chunks:
                # self.logger.info(f"Creating embedding for chunk: {chunk[:50]}...")
                response = self.client.embeddings.create(input=chunk, model=model)
                embeddings.append(response.data[0].embedding)
                # self.logger.info("Embedding created successfully for a chunk.")

            self.logger.info("Embeddings created successfully.")
            # Concatenate all chunk embeddings into a single embedding vector
            concatenated_embedding = np.mean(embeddings, axis=0)
            return concatenated_embedding

        except OpenAIError as e:
            self.logger.error(f"OpenAI error during embedding creation: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during embedding creation: {str(e)}", exc_info=True)
            return None


    def create_embeddings_for_faiss(self, texts, model="text-embedding-ada-002", chunk_size=1000):
        """
        Create embeddings for a list of texts and add them to a FAISS index.

        Args:
            texts (list of str): List of texts to create embeddings for.
            model (str): The model to use for creating embeddings. Default is "text-embedding-ada-002".
            chunk_size (int): The maximum number of tokens in each chunk.

        Returns:
            tuple: A tuple containing the FAISS index and the list of successfully embedded texts.
        """
        embeddings = []
        successful_texts = []
        self.logger.info("Starting the embedding creation process.")
        for text in texts:
            try:
                embedding = self.create_embeddings(text, model=model, chunk_size=chunk_size)
                if embedding is not None:
                    embeddings.append(embedding)
                    successful_texts.append(text)
                else:
                    self.logger.warning(f"Failed to create embedding for text: {text[:50]}...")
            except Exception as e:
                self.logger.error(f"Error creating embedding for text: {text[:50]}... Error: {str(e)}")

        if not embeddings:
            self.logger.error("No valid embeddings were created. Check your texts and embedding function.")
            raise ValueError("No valid embeddings were created. Check your texts and embedding function.")

        try:
            embeddings_array = np.array(embeddings).astype('float32')
            dimension = len(embeddings[0])
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings_array)
            self.logger.info(f"Number of vectors in FAISS index: {index.ntotal}")
        except Exception as e:
            self.logger.error(f"Error creating or adding embeddings to FAISS index: {str(e)}")
            raise

        return index, successful_texts
