from jinja2 import Environment, FileSystemLoader, select_autoescape

from ...config import EMBEDDING_CONTENT_TEMPLATES_PATH


def render_embedding_content(metadata: dict, metadata_type: str, searchpath: str = None):
    """
    Render the content for a metadata type using a Jinja2 template.
    The content is used to generate vector embeddings for the metadata.
    The template is loaded from the `searchpath`, which defaults to the
    `EMBEDDING_CONTENT_TEMPLATES_PATH` environment variable if not provided explicitly.

    Args:
        metadata (dict): The metadata to render.
        metadata_type (str): The type of metadata.
        searchpath (str): The path to search for the Jinja2 template.

    Returns:
        str: The rendered content.
    """

    # Load the Jinja2 environment
    searchpath = searchpath or EMBEDDING_CONTENT_TEMPLATES_PATH

    env = Environment(loader=FileSystemLoader(searchpath=searchpath), autoescape=select_autoescape())

    template_name = f"{metadata_type}_page_content.jinja2"

    # Load the template
    template = env.get_template(template_name)

    # Render the template with metadata
    page_content = template.render(metadata)

    return page_content
