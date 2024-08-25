# Description: Utility functions for metadata
import json

from ..paths import get_metadata_ids_path


def get_idno(metadata: dict, metadata_type: str) -> str:
    if metadata_type == "indicator":
        idno = metadata["series_description"]["idno"]
    elif metadata_type == "document":
        idno = metadata["document_description"]["title_statement"]["idno"]
    else:
        raise ValueError(f"Type {metadata_type} not supported")

    return idno


def get_metadata_ids(metadata_type: str) -> list[dict]:
    """
    Get the metadata ids collected from the metadata catalog for the given type.
    """

    fpath = get_metadata_ids_path(metadata_type=metadata_type)

    with open(fpath) as f:
        metadata_ids = json.load(f)

    return metadata_ids
