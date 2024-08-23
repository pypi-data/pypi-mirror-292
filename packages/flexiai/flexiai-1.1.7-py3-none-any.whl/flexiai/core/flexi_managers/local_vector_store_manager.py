# flexiai/core/flexi_managers/local_vector_store_manager.py
import os
import numpy as np
import faiss
import json


class LocalVectorStoreManager:
    """
    LocalVectorStoreManager handles the saving, loading, and updating of local vector stores using FAISS.

    Attributes:
        logger (logging.Logger): The logger for logging information and errors.
    """

    def __init__(self, client, logger, embedding_manager):
        """
        Initializes the LocalVectorStoreManager with the logger.

        Args:
            client: The client object for interacting with the backend.
            logger (logging.Logger, optional): Logger for logging information and errors. Defaults to None.
            embedding_manager (EmbeddingManager): The embedding manager for creating embeddings.
        """
        self.client = client
        self.logger = logger
        self.embedding_manager = embedding_manager
        

    def save_vector_store(self, index, file_path, metadata):
        """
        Saves the FAISS index and metadata to the specified file path.

        Args:
            index (faiss.Index): The FAISS index to be saved.
            file_path (str): The path where the index will be saved.
            metadata (dict): The metadata to be saved.
        """
        try:
            self.logger.info(f"Saving vector store to {file_path}")
            faiss.write_index(index, file_path)
            self.logger.info(f"Vector store saved to {file_path}")
            
            # Save metadata
            metadata_path = file_path + ".meta"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f)
            self.logger.info(f"Metadata saved to {metadata_path}")
        except Exception as e:
            self.logger.error(f"Error saving vector store to {file_path}: {str(e)}", exc_info=True)
            raise


    def load_vector_store(self, file_path):
        """
        Loads the FAISS index and metadata from the specified file path.

        Args:
            file_path (str): The path from where the index will be loaded.

        Returns:
            tuple: A tuple containing the loaded FAISS index and metadata.
        """
        try:
            self.logger.info(f"Loading vector store from {file_path}")
            index = faiss.read_index(file_path)
            self.logger.info(f"Vector store loaded from {file_path}")

            # Load metadata
            metadata_path = file_path + ".meta"
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            self.logger.info(f"Metadata loaded from {metadata_path}")
            
            return index, metadata
        except Exception as e:
            self.logger.error(f"Error loading vector store from {file_path}: {str(e)}", exc_info=True)
            raise


    def rebuild_faiss_index(self, vectors, dimension):
        """
        Rebuilds a FAISS index with the given vectors and dimension.

        Args:
            vectors (list): List of vectors to be added to the index.
            dimension (int): Dimension of the vectors.

        Returns:
            faiss.Index: The rebuilt FAISS index.
        """
        try:
            self.logger.info(f"Rebuilding FAISS index with dimension: {dimension}")
            index = faiss.IndexFlatL2(dimension)
            index.add(np.array(vectors).astype('float32'))
            self.logger.info(f"Rebuilt FAISS index with {index.ntotal} vectors.")
            return index
        except Exception as e:
            self.logger.error(f"Error rebuilding FAISS index: {str(e)}", exc_info=True)
            raise


    def extract_vectors_from_index(self, index):
        """
        Extracts vectors from the given FAISS index.

        Args:
            index (faiss.Index): The FAISS index to extract vectors from.

        Returns:
            list: List of extracted vectors.
        """
        try:
            self.logger.info("Extracting vectors from FAISS index")
            vectors = [index.reconstruct(i) for i in range(index.ntotal)]
            return vectors
        except Exception as e:
            self.logger.error(f"Error extracting vectors from FAISS index: {str(e)}", exc_info=True)
            raise


    def update_vector_in_index(self, index, old_vector, new_vector):
        """
        Updates a vector in the FAISS index.

        Args:
            index (faiss.Index): The FAISS index.
            old_vector (np.ndarray): The old vector to be replaced.
            new_vector (np.ndarray): The new vector to replace the old vector.

        Returns:
            faiss.Index: The updated FAISS index.
        """
        try:
            self.logger.info("Updating vector in FAISS index")
            vectors = self.extract_vectors_from_index(index)
            updated_vectors = [new_vector if np.array_equal(v, old_vector) else v for v in vectors]
            dimension = len(vectors[0])
            updated_index = self.rebuild_faiss_index(updated_vectors, dimension)
            self.logger.info("Vector updated in FAISS index successfully")
            return updated_index
        except Exception as e:
            self.logger.error(f"Error updating vector in FAISS index: {str(e)}", exc_info=True)
            raise


    def remove_vector_from_index(self, index, vector_to_remove, metadata):
        """
        Removes a vector from the FAISS index.

        Args:
            index (faiss.Index): The FAISS index.
            vector_to_remove (np.ndarray): The vector to be removed.
            metadata (dict): Metadata of the index.

        Returns:
            tuple: A tuple containing the updated FAISS index and the name of the removed file.
        """
        try:
            self.logger.info("Removing vector from FAISS index")
            vectors = self.extract_vectors_from_index(index)
            updated_vectors = []
            removed_file_name = None
            
            for i, v in enumerate(vectors):
                if not np.array_equal(v, vector_to_remove):
                    updated_vectors.append(v)
                else:
                    removed_file_name = metadata[str(i)]
                    del metadata[str(i)]
            
            dimension = len(vectors[0])
            updated_index = self.rebuild_faiss_index(updated_vectors, dimension)
            self.logger.info("Vector removed from FAISS index successfully")
            print(f"Vector removed from FAISS index successfully. Removed file: {removed_file_name}")
            
            return updated_index, removed_file_name
        except Exception as e:
            self.logger.error(f"Error removing vector from FAISS index: {str(e)}", exc_info=True)
            raise


    def map_vector_store(self, index, num_elements=5):
        """
        Maps and prints the vectors in the FAISS index.

        Args:
            index (faiss.Index): The FAISS index to be mapped.
            num_elements (int): The number of elements to print from each vector. Default is 5.
        """
        try:
            self.logger.info("Mapping vector store")
            vectors = self.extract_vectors_from_index(index)
            for i, vec in enumerate(vectors):
                self.logger.info(f"Vector {i}: {vec[:num_elements]}...")
                print(f"Vector {i}: {vec[:num_elements]}...")
            self.logger.info("Vector store mapping completed successfully")
        except Exception as e:
            self.logger.error(f"Error during vector store mapping: {str(e)}", exc_info=True)
            raise


    def read_corpus_from_directory(self, directory_path):
        """
        Reads all text files from the specified directory and returns their contents.

        Args:
            directory_path (str): The directory path to read files from.

        Returns:
            list: A list of tuples containing file paths and their contents.
        """
        self.logger.info(f"Reading corpus from directory: {directory_path}")
        corpus = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        corpus.append((file_path, content))
                        self.logger.info(f"File read successfully: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Error reading file {file_path}: {str(e)}", exc_info=True)
        return corpus


    def create_embeddings_from_file(self, file_path, chunk_size=1000):
        """
        Creates embeddings for the content of the specified file.

        Args:
            file_path (str): The path of the file to create embeddings for.
            chunk_size (int): The maximum number of tokens in each chunk.

        Returns:
            np.ndarray: The created embeddings.
        """
        try:
            self.logger.info(f"Creating embeddings from file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            embedding = self.embedding_manager.create_embeddings(content, chunk_size=chunk_size)
            self.logger.info("Embedding created successfully from file")
            print(f"Embedding created for file: {file_path}")
            return embedding
        except Exception as e:
            self.logger.error(f"Error creating embedding from file {file_path}: {str(e)}", exc_info=True)
            raise


    def cosine_similarity(self, vec1, vec2):
        """
        Calculates the cosine similarity between two vectors.

        Args:
            vec1 (np.ndarray): The first vector.
            vec2 (np.ndarray): The second vector.

        Returns:
            float: The cosine similarity between the vectors.
        """
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) 


    def verify_similarity_scores(self, query_embedding, embeddings, indices, corpus):
        """
        Verifies the similarity scores between the query embedding and a set of embeddings.

        Args:
            query_embedding (np.ndarray): The query embedding.
            embeddings (list of np.ndarray): The list of embeddings to compare against.
            indices (list of int): The indices of the embeddings to compare.
            corpus (list): The corpus containing the documents.
        """
        try:
            self.logger.info("Verifying similarity scores")
            for idx in indices:
                similarity = self.cosine_similarity(query_embedding, embeddings[idx])
                self.logger.info(f"Document: {corpus[idx][0]}, Similarity: {similarity:.4f}")
                print(f"Document: {corpus[idx][0]}, Similarity: {similarity:.4f}")
            self.logger.info("Similarity scores verification passed.")
        except Exception as e:
            self.logger.error(f"Error during similarity scores verification: {str(e)}")


    def print_metadata(self, file_path):
        """
        Prints the metadata from the specified file path.

        Args:
            file_path (str): The path to the metadata file.

        Returns:
            dict: The metadata.
        """
        try:
            # Load metadata
            metadata_path = file_path + ".meta"
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"Metadata from {metadata_path}:")
            print(json.dumps(metadata, indent=4))
            return metadata
        except Exception as e:
            self.logger.error(f"Error loading metadata from {metadata_path}: {str(e)}", exc_info=True)
            raise


    def replace_text_in_file_and_update_vector_store(self, file_path, old_text, new_text, index, metadata, save_path):
        """
        Replaces text in a file, updates the vector in the vector store, and saves the updated vector store.

        Args:
            file_path (str): The path of the file to update.
            old_text (str): The old text to be replaced.
            new_text (str): The new text to replace the old text.
            index (faiss.Index): The FAISS index.
            metadata (dict): Metadata of the index.
            save_path (str): The path where the updated vector store will be saved.

        Returns:
            tuple: The updated FAISS index and the new embedding.
        """
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create embeddings for the old and new texts
            old_embedding = self.embedding_manager.create_embeddings(old_text)
            new_embedding = self.embedding_manager.create_embeddings(new_text)

            # Find the index of the old vector
            old_vector_index = None
            for idx, path in metadata.items():
                if path == file_path:
                    old_vector_index = int(idx)
                    break

            if old_vector_index is None:
                raise ValueError(f"File {file_path} not found in the metadata.")

            # Calculate similarity before replacement
            old_vector = index.reconstruct(old_vector_index)
            similarity_before = self.cosine_similarity(old_vector, old_embedding)

            # Print old sentence and embedding
            self.print_sentence_and_embedding(old_text, old_vector, "Old")
            print(f"Similarity before replacement: {similarity_before:.4f}")

            # Replace old text with new text in the file content
            new_content = content.replace(old_text, new_text)

            # Update the vector in the index
            updated_index = self.update_vector_in_index(index, old_vector, new_embedding)

            # Calculate similarity after replacement
            new_vector = updated_index.reconstruct(old_vector_index)
            similarity_after = self.cosine_similarity(new_vector, new_embedding)

            # Print new sentence and embedding
            self.print_sentence_and_embedding(new_text, new_vector, "New")
            print(f"Similarity after replacement: {similarity_after:.4f}")

            # Save the updated index and metadata
            self.save_vector_store(updated_index, save_path, metadata)
            self.logger.info("Updated vector store after replacing text in the file")
            print("Updated vector store after replacing text in the file")

            return updated_index, new_embedding

        except Exception as e:
            self.logger.error(f"Error replacing text in file and updating vector store: {str(e)}", exc_info=True)
            print(f"Error replacing text in file and updating vector store: {str(e)}")



    def search_for_text_in_vector_store(self, text, index):
        """
        Searches for a specific text embedding in the vector store.

        Args:
            text (str): The text to search for.
            index (faiss.Index): The FAISS index.

        Returns:
            tuple: Indices and distances of the search results.
        """
        try:
            query_embedding = self.embedding_manager.create_embeddings(text)
            indices, distances = self.query_vector_store(index, query_embedding, k=5)
            return indices, distances
        except Exception as e:
            self.logger.error(f"Error searching for text in vector store: {str(e)}", exc_info=True)
            print(f"Error searching for text in vector store: {str(e)}")
            return [], []
        

    def query_vector_store(self, index, query_embedding, k=5):
        """
        Queries the vector store with a given embedding.

        Args:
            index (faiss.Index): The FAISS index.
            query_embedding (np.ndarray): The query embedding.
            k (int): The number of nearest neighbors to retrieve.

        Returns:
            tuple: Indices and distances of the nearest neighbors.
        """
        try:
            self.logger.info("Querying vector store")
            query_embedding = np.array(query_embedding).astype('float32').reshape(1, -1)
            D, I = index.search(query_embedding, k)
            self.logger.info(f"Query results: indices={I[0]}, distances={D[0]}")
            return I[0], D[0]
        except Exception as e:
            self.logger.error(f"Error querying vector store: {str(e)}", exc_info=True)
            raise


    def print_sentence_and_embedding(self, sentence, embedding, label, num_elements=5):
        """
        Prints a sentence and its embedding.

        Args:
            sentence (str): The sentence.
            embedding (np.ndarray): The embedding of the sentence.
            label (str): A label for the sentence (e.g., "Old" or "New").
            num_elements (int): The number of elements to print from the embedding. Default is 5.
        """
        print(f"{label} sentence: {sentence}")
        print(f"{label} embedding (first {num_elements} elements): {embedding[:num_elements]}\n")
