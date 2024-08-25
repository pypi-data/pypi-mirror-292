# config.py
import os
from pathlib import Path

BASE_PATH = Path(__file__).parent
DATA_PATH = Path(os.getenv("AI4DATA_DATA_PATH", BASE_PATH / "data"))

# The URL to the API endpoint of the metadata catalog
METADATA_CATALOG_URL = os.getenv("AI4DATA_METADATA_CATALOG_URL", "https://data-compass.ihsn.org/index.php")


EMBEDDING_MODEL = os.getenv("AI4DATA_EMBEDDING_MODEL", "avsolatorio/GIST-Embedding-v0")
EMBEDDING_BATCH_SIZE = int(os.getenv("AI4DATA_EMBEDDING_BATCH_SIZE", 64))
EMBEDDING_DEVICE = os.getenv("AI4DATA_EMBEDDING_DEVICE", None)
EMBEDDING_SHOW_PROGRESS = os.getenv("AI4DATA_EMBEDDING_SHOW_PROGRESS", True)

if isinstance(EMBEDDING_SHOW_PROGRESS, str):
    EMBEDDING_SHOW_PROGRESS = EMBEDDING_SHOW_PROGRESS.lower() == "true"

# The path to the Jinja2 templates for rendering metadata content.
# This can be set as an environment variable or defaults to the current directory.

EMBEDDING_CONTENT_TEMPLATES_PATH = os.getenv(
    "AI4DATA_EMBEDDING_CONTENT_TEMPLATES_PATH", str(Path(__file__).parent / "metadata" / "templates")
)


QDRANT_HOST = os.getenv("AI4DATA_QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("AI4DATA_QDRANT_PORT", 6333))
