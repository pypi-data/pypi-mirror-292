import json
from typing import Callable

import httpx
from fire import Fire
from tqdm.auto import tqdm

from ..config import METADATA_CATALOG_URL
from ..paths import get_metadata_cache_path, get_metadata_ids_path


def get_metadata_json(idno: str, metadata_type: str = None, force: bool = False) -> dict:
    """
    Retrieve metadata from a cache or fetch it from the catalog if not cached or if forced.

    Args:
        idno (str): The ID number of the metadata to retrieve.
        metadata_type (str, optional): The type of metadata to retrieve, used for caching. If None, caching is bypassed. Defaults to None.
        force (bool, optional): If True, forces a fresh retrieval of the metadata even if cached. Defaults to False.

    Returns:
        dict: The metadata associated with the given ID number.

    Raises:
        httpx.HTTPStatusError: If the HTTP request to fetch metadata fails.
        IOError: If reading from or writing to the cache file fails.
    """
    cache_path = get_metadata_cache_path(idno, metadata_type) if metadata_type else None

    if cache_path and not force and cache_path.exists():
        try:
            with cache_path.open("r") as cache_file:
                return json.load(cache_file)
        except OSError as e:
            print(f"Failed to read cache file {cache_path}: {e}")

    # Fetch the metadata from the remote service
    try:
        response = httpx.get(f"{METADATA_CATALOG_URL}/api/catalog/json/{idno}")
        response.raise_for_status()
        metadata: dict = response.json()

        if metadata.get("type", None) == "timeseries":
            metadata["type"] = "indicator"

        if metadata_type:
            assert (
                metadata.get("type", None) == metadata_type
            ), f"The metadata {metadata.get('type')} does not match the requested type: {metadata_type}"

    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Failed to fetch metadata for ID {idno}: {e}")

    # Cache the metadata for future use, if caching is enabled
    if cache_path:
        try:
            with cache_path.open("w") as cache_file:
                json.dump(metadata, cache_file, indent=2)
        except OSError as e:
            print(f"Failed to write cache file {cache_path}: {e}")

    return metadata


def search_metadata(params: dict = None) -> dict:
    """
    Search metadata in the metadata catalog using provided search parameters.

    Args:
        params (dict, optional): Parameters for the search query. Defaults to None.

    Returns:
        dict: The search results from the metadata catalog.
    """
    response = httpx.get(f"{METADATA_CATALOG_URL}/api/catalog/search", params=params)
    response.raise_for_status()
    data = response.json().get("result", {})
    return data


def get_ids_type(result: dict = None) -> dict:
    """
    Extract ID, ID number, and type information from a metadata catalog result.

    Args:
        result (dict, optional): A single result item from the metadata catalog. Defaults to None.

    Returns:
        dict: A dictionary containing the 'id', 'idno', and 'type' of the result.
    """
    if result is None:
        return dict(id=None, idno=None, type=None)

    metadata_type = result.get("type", None)
    if metadata_type == "timeseries":
        metadata_type = "indicator"

    return dict(id=result.get("id", None), idno=result.get("idno", None), type=metadata_type)


def get_metadata_ids(params: dict = None, search_metadata_func=search_metadata) -> list:
    """
    Retrieve all metadata IDs from the metadata catalog based on search parameters.

    Args:
        params (dict, optional): Parameters for the search query. Defaults to None.
        search_metadata_func (function, optional): The function to use for searching metadata.
            Can be the raw function or a Prefect task. Defaults to search_metadata.

    Returns:
        list: A list of dictionaries containing 'id', 'idno', and 'type' for each metadata entry.
    """

    default_params = dict(sk="", ps=100, type="timeseries", sort_by="year", sort_order="asc")
    params = {**default_params, **(params or {})}

    all_metadata_ids = []

    params["page"] = 1
    num_per_page = int(params["ps"])

    data = search_metadata_func(params)
    all_metadata_ids.extend([get_ids_type(row) for row in data.get("rows", [])])

    all_pages = int(data.get("found", 0)) // num_per_page + 1

    for page in tqdm(range(2, all_pages + 1)):
        params["page"] = page
        data = search_metadata_func(params)
        all_metadata_ids.extend([get_ids_type(row) for row in data.get("rows", [])])

    return all_metadata_ids


def save_metadata_ids(metadata_ids: list, dtype: str) -> None:
    """
    Save the metadata IDs to a JSON file.

    Args:
        metadata_ids (list): A list of metadata ID dictionaries to save.
        dtype (str): The type of metadata (e.g., 'indicator', 'document').
    """
    if metadata_ids is None or len(metadata_ids) == 0:
        return

    fpath = get_metadata_ids_path(dtype)
    fpath.parent.mkdir(parents=True, exist_ok=True)

    with open(fpath, "w") as f:
        json.dump(metadata_ids, f, indent=2)


def scrape_all_ids(
    get_metadata_ids_func: Callable = get_metadata_ids,
    search_metadata_func: Callable = search_metadata,
    save_metadata_ids_func: Callable = save_metadata_ids,
    **kwargs,
):
    """
    Scrape all metadata IDs from the metadata catalog based on the provided parameters.

    Args:
        get_metadata_ids_func (Callable, optional): Function or task to fetch metadata IDs.
        search_metadata_func (Callable, optional): Function or task to search metadata.
        save_metadata_ids_func (Callable, optional): Function or task to save metadata IDs.
        **kwargs: Arbitrary keyword arguments representing search parameters.
    """
    params = kwargs

    assert "ps" in params, "The number of items per page is required"
    assert "type" in params, "The type of metadata is required, e.g., timeseries, document, geospatial, etc."

    if params["type"] == "indicator":
        params["type"] = "timeseries"

    dtype = params["type"]
    if dtype == "timeseries":
        dtype = "indicator"

    # Use dependency injection to choose between direct function or Prefect task
    metadata_ids = get_metadata_ids_func(params, search_metadata_func=search_metadata_func)
    print(f"Total metadata ids: {len(metadata_ids)}")

    save_metadata_ids_func(metadata_ids, dtype)


def main(**kwargs):
    scrape_all_ids(**kwargs)


if __name__ == "__main__":
    Fire(main)
