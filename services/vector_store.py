import os
import shutil
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import JSONLoader, PyPDFLoader, CSVLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class VectorStoreService:
    def __init__(self):
        self.base_dir = os.getenv('DB_DIR')

    def _validate_store_name(self, store_name: str) -> None:
        """
        Validates if a vector store name is valid.

        Args:
            store_name (str): The name of the vector store.
        """
        if not isinstance(store_name, str):
            raise ValueError("Store name must be a string.")
        if len(store_name) == 0:
            raise ValueError("Store name cannot be empty.")

    def _validate_store_exists(self, existing_stores: list[str], store_name: str) -> None:
        """
        Validates if a vector store already exists.

        Args:
            existing_stores (list[str]): A list of existing vector stores.
            store_name (str): The name of the vector store to check.
        """
        if not isinstance(existing_stores, list) or not all(isinstance(store, str) for store in existing_stores):
            raise ValueError("Existing stores must be a non-empty list of strings.")
        if store_name not in existing_stores:
            raise ValueError(f"Vector store '{store_name}' does not exist.")

    def _validate_file_type(self, file_type: str) -> None:
        """
        Validates if a file type is supported.

        Args:
            file_type (str): The type of the file.
        """
        if not isinstance(file_type, str):
            raise ValueError("File type must be a string.")
        supported_types = ['json', 'pdf', 'csv', 'web']
        if file_type not in supported_types:
            raise ValueError(f"Unsupported file type: {file_type}.")

    def _load_file(self, file_path: str, file_type: str) -> dict:
        """
        Loads a file into memory.

        Args:
            file_path (str): The path to the file.
            file_type (str): The type of the file.

        Returns:
            dict: A dictionary containing the loaded file data.
        """
        self._validate_file_type(file_type)
        
        if file_type == 'json':
            return JSONLoader(file_path=file_path, jq_schema='.', text_content=False).load()
        elif file_type == 'pdf':
            return PyPDFLoader(file_path=file_path).load()
        elif file_type == 'csv':
            return CSVLoader(file_path=file_path).load()
        elif file_type == 'web':
            return WebBaseLoader(file_path).load()

    def get_all(self) -> list[str]:
        """
        Retrieves a list of all existing vector stores.

        Returns:
            list[str]: A list of string representing the names of all vector stores.
        """
        base_dir = self.base_dir
        if not os.path.exists(base_dir):
            return []
        
        return [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

    def get(self, store_name: str) -> Chroma:
        """
        gets vector store by the given name.

        Args:
            store_name (str): The name of the vector store to be created.

        Returns:
            Chroma: An instance of `Chroma` representing the newly created vector store.
        """
        self._validate_store_name(store_name)
        
        if not self.exists(store_name):
            raise ValueError(f"Vector store '{store_name}' does not exist.")
        
        local_embeddings = OllamaEmbeddings(model=os.getenv("EMBEDDING_MODEL"), show_progress=True)
        return Chroma(
            collection_name=store_name,
            embedding_function=local_embeddings,
            persist_directory=os.path.join(self.base_dir, store_name)
        )

    def exists(self, store_name: str) -> bool:
        """
        Checks if a vector store already exists.

        Args:
            store_name (str): The name of the vector store to check.

        Returns:
            bool: True if the vector store exists, False otherwise.
        """
        existing_stores = self.get_all()
        return store_name in existing_stores

    def create(self, store_name: str) -> Chroma:
        """
        Creates a new vector store with the given name.

        Args:
            store_name (str): The name of the vector store to be created.

        Returns:
            Chroma: An instance of `Chroma` representing the newly created vector store.
        """
        self._validate_store_name(store_name)
        
        if self.exists(store_name):
            raise ValueError(f"Vector store '{store_name}' already exists.")
        
        local_embeddings = OllamaEmbeddings(model=os.getenv("EMBEDDING_MODEL"), show_progress=True)
        return Chroma(
            collection_name=store_name,
            embedding_function=local_embeddings,
            persist_directory=os.path.join(self.base_dir, store_name)
        )

    def update(self, file: str, store_name: str, file_type: str) -> None:
        """
        Updates a vector store with the given file.

        Args:
            file (str): The path to the file.
            store_name (str): The name of the vector store to be updated.
            file_type (str): The type of the file.
        """
        docs = self._load_file(file, file_type)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)

        local_embeddings = OllamaEmbeddings(model=os.getenv("EMBEDDING_MODEL"), show_progress=True)
        Chroma.from_documents(
            collection_name=store_name,
            documents=chunks,
            embedding=local_embeddings,
            persist_directory=os.path.join(self.base_dir, store_name)
        )

    def delete(self, store_name):
        """
        Deletes a vector store by removing its directory.

        Args:
            store_name (str): The name of the vector store to be deleted.
        """

        # Check if the vector store exists
        if not self.exists(store_name):
            raise ValueError(f"Vector store '{store_name}' does not exist.")

        # Get the path to the vector store directory
        store_dir = os.path.join(self.base_dir, store_name)

        try:
            # Attempt to remove the directory and all its contents
            shutil.rmtree(store_dir)
            
            print(f"Vector store '{store_name}' successfully deleted.")
        
        except OSError as e:
            # Handle any errors that occur during deletion
            raise ValueError(f"Failed to delete vector store '{store_name}': {e}")