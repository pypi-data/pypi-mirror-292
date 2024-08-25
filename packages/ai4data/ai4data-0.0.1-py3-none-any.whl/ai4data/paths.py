from pathlib import Path

from .commons import validate_type
from .config import DATA_PATH

METADATA_IDS_DIR = DATA_PATH / "metadata_ids"
INDEXED_IDS_DIR = DATA_PATH / "indexed_ids"
METADATA_CACHE_DIR = DATA_PATH / "metadata_cache"
DOCUMENT_CACHE_DIR = DATA_PATH / "document_cache"


def ensure_dir_exists(path: Path) -> Path:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


def construct_path(directory: Path, filename: str) -> Path:
    ensure_dir_exists(directory)
    return directory / filename


def get_metadata_ids_path(metadata_type: str) -> Path:
    metadata_type = validate_type(metadata_type)

    return construct_path(METADATA_IDS_DIR, f"metadata_ids_{metadata_type}.json")


def get_indexed_ids_path(metadata_type: str) -> Path:
    metadata_type = validate_type(metadata_type)

    return construct_path(INDEXED_IDS_DIR, f"indexed_ids_{metadata_type}.json")


def get_metadata_cache_path(idno: str, metadata_type: str) -> Path:
    return construct_path(METADATA_CACHE_DIR / metadata_type, f"{metadata_type}_{idno}.json")


def get_document_cache_path(idno: str, metadata_type: str) -> Path:
    return construct_path(DOCUMENT_CACHE_DIR / metadata_type, f"{metadata_type}_{idno}.pdf")
