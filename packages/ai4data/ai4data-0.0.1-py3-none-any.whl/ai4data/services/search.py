# This service implements the search functionalities.
from ai4data.indexing.embed import (
    EmbeddingModelSingleton,
    get_vector_store,
)

METADATA_TYPES = ["indicator", "document", "microdata", "geospatial"]


def semantic_search(
    query: str,
    filters: dict = None,
    page: int = 1,
    page_size: int = 10,
    batch_top_k: int = 1000,
) -> list[dict]:
    """
    Search for similar content to the query.

    If filters are provided, the search will be filtered based on the information in the filters.

    Otherwise, the search will be performed on all available content. We will retrieve the `batch_top_k` most similar content for each metadata type. Then, we will aggregate the results and return the `page_size` results starting from `page` based on the highest scores.

    Args:
        query (str): The query to search for.
        filters (dict, optional): Filters to apply to the search. Defaults to None.
        page (int, optional): The page number to retrieve. Defaults to 1.
        page_size (int, optional): The number of results to retrieve per page. Defaults to 10.
        batch_top_k (int, optional): The number of results to retrieve for each metadata type. Defaults to 1000.

    Returns:
        list[dict]: The search results.
    """

    filters = filters or {}

    metadata_types = filters.get("metadata_type", METADATA_TYPES)

    if not isinstance(metadata_types, list):
        metadata_types = [metadata_types]

    results = []

    for metadata_type in metadata_types:
        vector_store = get_vector_store(EmbeddingModelSingleton.get_instance(), metadata_type)
        results.extend(
            [
                dict(doc=doc, score=score)
                for doc, score in vector_store.similarity_search_with_score(query, k=batch_top_k)
            ]
        )

    # Sort the results by score and retrieve the requested page
    start = (page - 1) * page_size
    end = page * page_size

    results = sorted(results, key=lambda x: x["score"], reverse=True)[start:end]

    return results
