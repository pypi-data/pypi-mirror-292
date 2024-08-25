import gc

import numpy as np
import torch
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import SentenceTransformersTokenTextSplitter
from qdrant_client import QdrantClient

from ..config import (
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_DEVICE,
    EMBEDDING_MODEL,
    EMBEDDING_SHOW_PROGRESS,
    QDRANT_HOST,
    QDRANT_PORT,
)


def get_device(preferred_device: str = None) -> str:
    """
    Determine the appropriate device to run the model on.

    Args:
        preferred_device (str, optional): Preferred device specified by the user.

    Returns:
        str: The device to be used ('cuda', 'mps', or 'cpu').
    """
    if preferred_device:
        return preferred_device

    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"

    return "cpu"


class EmbeddingModelSingleton:
    _instance = None
    _model_kwargs = None

    @classmethod
    def get_instance(
        cls,
        model_name: str = EMBEDDING_MODEL,
        device: str = EMBEDDING_DEVICE,
        model_kwargs: dict = None,
        encode_kwargs: dict = None,
        show_progress: bool = EMBEDDING_SHOW_PROGRESS,
        reinitialize: bool = False,
    ) -> HuggingFaceEmbeddings:
        """
        Return a singleton instance of HuggingFaceEmbeddings, with an option to reinitialize.

        Args:
            model_name (str): The name of the model.
            device (str, optional): The device to run the model on. Defaults to None.
            model_kwargs (dict, optional): Additional keyword arguments for model initialization.
            encode_kwargs (dict, optional): Additional keyword arguments for encoding.
            show_progress (bool, optional): Whether to show progress bars. Defaults to True.
            reinitialize (bool, optional): If True, forces reinitialization of the singleton instance. Defaults to False.

        Returns:
            HuggingFaceEmbeddings: The singleton embedding model instance.
        """
        model_kwargs = model_kwargs or {}
        model_kwargs["device"] = get_device(device)
        encode_kwargs = encode_kwargs or {
            "normalize_embeddings": True,
            "batch_size": EMBEDDING_BATCH_SIZE,
        }

        if (
            reinitialize
            or cls._instance is None
            or cls._instance.model_name != model_name
            or cls._instance.encode_kwargs != encode_kwargs
            or cls._model_kwargs != model_kwargs
        ):
            cls._clear_instance()

            cls._instance = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs,
                show_progress=show_progress,
            )
            cls._model_kwargs = model_kwargs

        if cls._instance.show_progress != show_progress:
            cls._instance.show_progress = show_progress

        return cls._instance

    @classmethod
    def _clear_instance(cls):
        """
        Clear the current singleton instance and free GPU memory.
        """
        if cls._instance is not None:
            # Delete the instance reference
            del cls._instance

            # Clear GPU memory if the model was loaded on a GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Optionally force garbage collection
            gc.collect()

    @classmethod
    def reset_instance(cls):
        """
        Reset the singleton instance, forcing it to be reinitialized the next time get_instance is called.
        """
        cls._clear_instance()
        cls._instance = None
        cls._model_kwargs = None


class TextSplitterSingleton:
    _instance = None
    _kwargs = None

    @classmethod
    def get_instance(cls, model_name: str = EMBEDDING_MODEL, **kwargs) -> SentenceTransformersTokenTextSplitter:
        """
        Return a singleton instance of SentenceTransformersTokenTextSplitter.

        Args:
            model_name (str): The name of the model to use for tokenization.
            **kwargs: Additional keyword arguments for the text splitter.

        Returns:
            SentenceTransformersTokenTextSplitter: The singleton text splitter instance.
        """

        kwargs = kwargs or {"chunk_overlap": 0}

        if cls._instance is None or cls._instance.model_name != model_name or cls._kwargs != kwargs:
            cls._instance = SentenceTransformersTokenTextSplitter(model_name=model_name, **kwargs)
            cls._kwargs = kwargs

        return cls._instance

    @classmethod
    def reset_instance(cls):
        """
        Reset the singleton instance, forcing it to be reinitialized the next time get_instance is called.
        """
        cls._instance = None
        cls._kwargs = None


class QdrantClientSingleton:
    _instance = None

    @classmethod
    def get_instance(cls, host: str = QDRANT_HOST, port: int = QDRANT_PORT, reinitialize: bool = False) -> QdrantClient:
        """
        Return a singleton instance of QdrantClient. Once initialized, the instance will be reused despite different host/port parameters. Use, force reinitialization by setting reinitialize to True to change the host/port.

        Args:
            host (str, optional): The host of the Qdrant service. Defaults to "localhost".
            port (int, optional): The port of the Qdrant service. Defaults to 6333.
            reinitialize (bool, optional): If True, forces reinitialization of the singleton instance. Defaults to False.

        Returns:
            QdrantClient: The singleton Qdrant client instance.
        """
        if cls._instance is None or reinitialize:
            cls._instance = QdrantClient(host=host, port=port)

        # Ensure the host and port are correct and make the user aware if they are not.
        assert cls._instance.http.client.host.endswith(f"{host}:{port}")

        return cls._instance

    @classmethod
    def reset_instance(cls):
        """
        Reset the singleton instance, forcing it to be reinitialized the next time get_instance is called.
        """
        cls._instance = None


def get_collection_name(embedding_model: HuggingFaceEmbeddings, metadata_type: str) -> str:
    """
    Generate a collection name based on the embedding model name and metadata_type.

    Args:
        embedding_model (HuggingFaceEmbeddings): The embedding model used.
        metadata_type (str): The metadata_type of the data.

    Returns:
        str: The generated collection name.
    """
    model_name = embedding_model.model_name.replace("/", "__")
    return f"{model_name}__{metadata_type}"


def get_vector_store(embedding_model: HuggingFaceEmbeddings, metadata_type: str) -> QdrantVectorStore:
    """
    Return a Qdrant vector store for the specified embedding model and metadata_type.

    Args:
        embedding_model (HuggingFaceEmbeddings): The embedding model used.
        metadata_type (str): The metadata_type of the data.

    Returns:
        Qdrant: The vector store.
    """
    collection_name = get_collection_name(embedding_model, metadata_type)
    return QdrantVectorStore(
        client=QdrantClientSingleton.get_instance(), collection_name=collection_name, embedding=embedding_model
    )


def get_embeddings(docs: list[str], embedding_model: HuggingFaceEmbeddings, as_array: bool = True) -> np.ndarray:
    """
    Generate embeddings for a list of documents using the provided embedding model.

    Args:
        docs (list[str]): The documents to embed.
        embedding_model (HuggingFaceEmbeddings): The embedding model to use.
        as_array (bool, optional): Whether to return the embeddings as a NumPy array. Defaults to True.

    Returns:
        np.ndarray: The embeddings.
    """
    embeddings = embedding_model.embed_documents(docs)

    if as_array:
        return np.array(embeddings)

    return embeddings


# Load the singleton instances using the default parameters.
embedding_model = EmbeddingModelSingleton.get_instance()
qdrant_client = QdrantClientSingleton.get_instance()
text_splitter = TextSplitterSingleton.get_instance()
