from abc import ABC, abstractmethod

from langchain_core.documents import Document as LangchainDocument

from ..processors.document import get_doc_reps, load_pdf
from ..scraper.document import cache_download_pdf
from ..scraper.metadata import get_metadata_json
from .templates.render import render_embedding_content


class Metadata(ABC):
    def __init__(self, metadata: dict, metadata_type: str = None, searchpath: str = None):
        """
        Initialize the Metadata handler.

        Args:
            metadata (dict): The metadata dictionary.
            metadata_type (str, optional): Type of metadata (e.g., 'document', 'indicator').
            searchpath (str, optional): Path used for searching or rendering templates. Defaults to None.
        """
        self._metadata = metadata
        self.type = metadata_type
        self.searchpath = searchpath
        self._metadata_langdoc = None

    @property
    def metadata(self) -> dict:
        """
        Retrieve the metadata.

        Returns:
            dict: The metadata.
        """
        return self._metadata

    @property
    def metadata_langdoc(self) -> LangchainDocument:
        """
        Retrieve the LangChain document for the metadata.

        Returns:
            LangchainDocument: A LangChain document.
        """
        if self._metadata_langdoc is None:
            self._metadata_langdoc = LangchainDocument(page_content=self.embedding_content(), metadata=self.metadata)

        return self._metadata_langdoc

    def embedding_content(self) -> str:
        """
        Generate the embedding content from the metadata.

        This content is used to generate embeddings.

        Returns:
            str: The content to be used for embedding.
        """
        embedding_content = render_embedding_content(self.metadata, self.type, searchpath=self.searchpath)
        return embedding_content.strip()

    @abstractmethod
    def get_langdocs(self) -> list[LangchainDocument]:
        """
        Retrieve the LangChain documents for the metadata.

        This method must be implemented by subclasses to return content that will be indexed based on the metadata type.

        Returns:
            list: A list of LangChain documents.
        """
        raise NotImplementedError("Subclasses must implement the get_langdocs method.")


class IndicatorMetadata(Metadata):
    def __init__(self, **kwargs):
        super().__init__(metadata_type="indicator", **kwargs)

    def get_langdocs(self) -> list[LangchainDocument]:
        """
        Retrieve the LangChain documents for the indicator metadata.

        Returns:
            list: A list of LangChain documents.
        """
        return [self.metadata_langdoc]


class DocumentMetadata(Metadata):
    """
    Ideas for how we should work with documents:

    - Include the title in generating the embeddings,
        - If the title is retrieved as the most relevant for a query,
        - we do not use it directly as the input to an LLM. Instead, we use the title to retrieve the document.
        - We then use the most relevant section of the document as the input to the LLM together with the title.

    - Contents considered for the embeddings:
        - Title + Abstract
        - Keywords
        - Sections of the document
    """

    def __init__(self, **kwargs):
        super().__init__(metadata_type="document", **kwargs)

    def get_doc_langdocs(self):
        """
        Retrieve the LangChain documents for the document metadata.

        Returns:
            list: A list of LangChain documents.
        """
        url = self.metadata.get("document_description", {}).get("url", None)
        docs = []

        if url:
            # Download the document pdf.
            # We only consider pdfs for now.
            pdf_path = cache_download_pdf(url, self.metadata.get("idno"), self.type)
            docs = load_pdf(pdf_path)

        return [LangchainDocument(page_content=doc.page_content, metadata=self.metadata) for doc in docs]

    def get_langdocs(self) -> list[LangchainDocument]:
        """
        Retrieve the LangChain documents for the document metadata.

        Returns:
            list: A list of LangChain documents.
        """
        langdocs = [self.metadata_langdoc]

        # Get the contents from the document itself
        doc_contents = self.get_doc_langdocs()
        doc_reps = []

        if doc_contents:
            # Get the document representations
            doc_reps = get_doc_reps(doc_contents)

        # Add the document contents to the metadata contents
        langdocs.extend(doc_reps)
        return langdocs


class MetadataLoader:
    def __init__(self, idno: str, metadata_type: str, force: bool = False, searchpath: str = None):
        """
        Initialize the MetadataLoader.

        Args:
            idno (str): The identifier number for fetching metadata.
            metadata_type (str): Type of metadata (e.g., 'document', 'indicator').
            force (bool, optional): If True, forces fetching the metadata from the catalog even if cached. Defaults to False.
            searchpath (str, optional): Path used for searching or rendering templates. Defaults to None.
        """
        self.idno = idno
        self.type = metadata_type
        self.force = force
        self.searchpath = searchpath
        self.metadata = self.load_metadata()

    def load_metadata(self) -> dict:
        """
        Load the metadata using the idno and metadata type.

        Returns:
            dict: The loaded metadata.
        """
        return get_metadata_json(self.idno, self.type, force=self.force)

    def get_metadata_handler(self) -> Metadata:
        """
        Get the appropriate Metadata handler class based on the type of metadata.

        Returns:
            Metadata: An instance of the appropriate Metadata subclass.
        """
        if self.type == "indicator":
            return IndicatorMetadata(metadata=self.metadata, searchpath=self.searchpath)
        elif self.type == "document":
            return DocumentMetadata(metadata=self.metadata, searchpath=self.searchpath)
        else:
            raise ValueError(f"Type {self.type} not supported")


def get_metadata_langdocs(
    idno: str, metadata_type: str, force: bool = False, searchpath: str = None
) -> list[LangchainDocument]:
    """
    Get the metadata documents for the given idno and metadata type.

    Args:
        idno (str): The identifier number.
        metadata_type (str): The type of metadata (e.g., 'indicator', 'document').
        force (bool, optional): If True, forces fetching the metadata from the catalog even if cached. Defaults to False.
        searchpath (str, optional): Path used for searching or rendering templates. Defaults to None.

    Returns:
        list: A list of LangChain documents.
    """
    loader = MetadataLoader(idno=idno, metadata_type=metadata_type, force=force, searchpath=searchpath)
    metadata_handler = loader.get_metadata_handler()
    return metadata_handler.get_langdocs()
