import json
from typing import Callable, Optional

from fire import Fire
from langchain_core.documents import Document as LangchainDocument
from langchain_qdrant import Qdrant
from prefect.utilities.annotations import quote
from tqdm.auto import tqdm

from ..metadata.handler import get_metadata_langdocs
from ..metadata.utils import get_idno, get_metadata_ids
from ..paths import get_indexed_ids_path
from .embed import EmbeddingModelSingleton, QdrantClientSingleton, get_collection_name


def save_indexed_ids(indexed_ids: list[dict], metadata_type: str = "indicator"):
    """
    Saves the given list of indexed IDs to the appropriate file based on metadata type.

    Args:
        indexed_ids (list[dict]): List of indexed ID dictionaries to save.
        metadata_type (str): The metadata type (e.g., 'indicator'). Defaults to 'indicator'.
    """
    fpath = get_indexed_ids_path(metadata_type=metadata_type)
    fpath.parent.mkdir(parents=True, exist_ok=True)
    with open(fpath, "a+") as f:
        for indexed_id in indexed_ids:
            f.write(json.dumps(indexed_id) + "\n")


def index_content(docs: list[LangchainDocument], metadata_type: str, force_recreate: bool = False):
    """
    Indexes content into Qdrant using the given documents and metadata type.

    Args:
        docs (list[LangchainDocument]): List of documents to be indexed.
        metadata_type (str): The type of metadata (e.g., 'indicator').
        force_recreate (bool): If True, forces recreation of the Qdrant collection. Defaults to False.
    """
    embedding_model = EmbeddingModelSingleton.get_instance()
    collection_name = get_collection_name(embedding_model, metadata_type)

    qdrant = Qdrant.from_documents(
        docs,
        embedding_model,
        url=QdrantClientSingleton.get_instance().http.client.host,
        prefer_grpc=True,
        collection_name=collection_name,
        force_recreate=force_recreate,
    )

    indexed_ids = [{"idno": get_idno(doc.metadata, doc.metadata["type"]), "type": doc.metadata["type"]} for doc in docs]

    save_indexed_ids(indexed_ids, metadata_type=metadata_type)

    qdrant.client.close()


def get_indexed_ids(metadata_type: str = "indicator"):
    """
    Retrieves a set of indexed IDs from the file corresponding to the given metadata type.

    Args:
        metadata_type (str): The metadata type (e.g., 'indicator'). Defaults to 'indicator'.

    Returns:
        set: A set of indexed IDs.
    """
    fpath = get_indexed_ids_path(metadata_type=metadata_type)
    if not fpath.exists():
        return []
    with open(fpath) as f:
        indexed_ids = [json.loads(line) for line in f.readlines() if line.strip()]
    return set(id["idno"] for id in (indexed_ids or []))


def load_index_content(
    metadata_ids: list[dict], metadata_type: str = "indicator", force_recreate: bool = False, index_content_func=None
):
    """
    Loads and indexes the content for the given list of metadata IDs.

    Args:
        metadata_ids (list[dict]): List of metadata ID dictionaries.
        metadata_type (str): The metadata type (e.g., 'indicator'). Defaults to 'indicator'.
        force_recreate (bool): If True, forces recreation of the Qdrant collection. Defaults to False.
        index_content_func (function): The function to use for indexing content (either Prefect task or regular function).
    """
    documents = []
    if force_recreate:
        metadata_id = metadata_ids.pop(0)
        index_content_func(
            get_metadata_langdocs(metadata_id, metadata_type),
            metadata_type=metadata_type,
            force_recreate=force_recreate,
        )

    for metadata_id in tqdm(metadata_ids, desc="Loading metadata content"):
        documents.extend(get_metadata_langdocs(metadata_id, metadata_type))

    index_content_func(documents, metadata_type=metadata_type, force_recreate=False)


def index(
    index_content_func: Callable = index_content,
    get_indexed_ids_func: Callable = get_indexed_ids,
    load_index_content_func: Callable = load_index_content,
    metadata_type: str = "indicator",
    batch_size: int = 128,
    size: Optional[int] = None,
    force_index: bool = False,
    is_prefect: bool = False,
) -> None:
    """
    Indexes metadata content into Qdrant for the given type in batches.

    This function orchestrates the indexing process, either using Prefect tasks or
    regular functions, based on the provided arguments.

    Args:
        index_content_func (Callable): Function or task used to index content into Qdrant. Defaults to the `index_content` function.
        get_indexed_ids_func (Callable): Function or task used to retrieve already indexed IDs. Defaults to the `get_indexed_ids` function.
        load_index_content_func (Callable): Function or task used to load and index metadata content. Defaults to the `load_index_content` function.
        metadata_type (str): The metadata type to index (e.g., 'indicator'). Defaults to 'indicator'.
        batch_size (int): The number of items to process in each batch. Defaults to 128.
        size (Optional[int]): The maximum number of items to process. If None, processes all items. Defaults to None.
        force_index (bool): If True, forces reindexing of all items, ignoring previously indexed content. Defaults to False.
        is_prefect (bool): If True, uses Prefect tasks for indexing. Defaults to False.

    Returns:
        None
    """

    # Retrieve indexed IDs or clear them if reindexing is forced
    if force_index:
        indexed_ids = []
        fpath = get_indexed_ids_path(metadata_type=metadata_type)
        fpath.unlink(missing_ok=True)
    else:
        indexed_ids = get_indexed_ids_func(metadata_type=metadata_type)

    # Retrieve metadata IDs for the specified type
    metadata_ids = get_metadata_ids(metadata_type=metadata_type)

    # Optionally limit the number of items to process
    if size:
        metadata_ids = metadata_ids[:size]

    # Filter out already indexed metadata IDs
    metadata_ids = [id for id in metadata_ids if id["idno"] not in indexed_ids]

    # Process metadata IDs in batches
    for i in tqdm(range(0, len(metadata_ids), batch_size), desc="Processing batches"):
        force_recreate = i == 0 and len(indexed_ids) == 0
        batch = metadata_ids[i : i + batch_size]

        # Quote the batch if using Prefect tasks
        batch = quote(batch) if is_prefect else batch

        load_index_content_func(
            batch, metadata_type=metadata_type, force_recreate=force_recreate, index_content_func=index_content_func
        )


def main(**kwargs):
    index(**kwargs)


if __name__ == "__main__":
    Fire(main)
