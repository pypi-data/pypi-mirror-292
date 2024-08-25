from io import StringIO
from typing import Union

import numpy as np
from bs4 import BeautifulSoup
from langchain_community.document_loaders.pdf import BasePDFLoader, PyMuPDFLoader
from langchain_core.documents import Document as LangchainDocument
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from tika import parser

from ..indexing.embed import embedding_model, text_splitter
from ..methods.semantic_cluster_embedding import semantic_cluster_embedding


# @task(log_prints=True)
def load_pdf(
    file_path: str, pdf_loader_cls: BasePDFLoader = PyMuPDFLoader, loader_kwargs: dict = None, load_kwargs: dict = None
) -> list[LangchainDocument]:
    """
    Load a PDF file and return a LangchainDocument object.

    Args:
        file_path: The path to the PDF file.
        pdf_loader_cls: The PDF loader class to use.
        loader_kwargs: The loader kwargs.
        load_kwargs: The load kwargs.

    Returns:
        A list of LangchainDocument objects.

    Raises:
        Exception: If an error occurs during loading.
    """
    try:
        loader_kwargs = loader_kwargs or {}
        load_kwargs = load_kwargs or {}

        loader = pdf_loader_cls(file_path, **loader_kwargs)
        docs = loader.load(**load_kwargs)

    except Exception as exception:
        print(f"load_pdf Exception {exception}: {file_path}")
        raise exception

    return docs


def merge_split_docs(docs: list[LangchainDocument], splitter) -> list[LangchainDocument]:
    """
    Merge the documents into one document, then split them into chunks defined in the splitter instance.

    NOTE: This removes the metadata from the documents and only keeps the metadata from the first document.
    TODO: Find a way to keep the PDF metadata. See: https://github.com/avsolatorio/data-use/blob/887e46ce24e27edac0658786dae0645571b889db/src/data_use/text_splitter.py

    Args:
        docs: The list of LangChain documents to merge and split.

    Returns:
        A list of LangchainDocument objects.
    """

    page_content = "\n\n".join([doc.page_content for doc in docs])

    chunks = splitter.split_text(page_content)
    metadata = docs[0].metadata

    return [LangchainDocument(page_content=chunk, metadata=metadata) for chunk in chunks]


def embed_documents(
    docs: list[Union[str, LangchainDocument]], embedding_model: HuggingFaceEmbeddings = embedding_model
) -> np.ndarray:
    """
    Embed the documents and return a list of embedded documents.

    Args:
        embedding_model: The embedding model from LangChain (HuggingFaceEmbeddings).
        docs: The list of documents to embed.
    """

    if isinstance(docs[0], LangchainDocument):
        docs = [doc.page_content for doc in docs]

    return np.array(embedding_model.embed_documents(docs))


# @task
def get_doc_reps(docs: list[LangchainDocument], embedding_model: HuggingFaceEmbeddings = embedding_model):
    """
    Get the document representations by merging and splitting the documents, then embedding them.

    Args:
        docs: The list of LangChain documents to merge and split.
        splitter: The text splitter to use.

    Returns:
        The document representations.
    """

    # Merge and split the documents
    split_docs = merge_split_docs(docs, text_splitter)

    # Embed the documents
    doc_reps = embed_documents(split_docs, embedding_model)

    # Cluster the document representations and get the cluster info
    cluster_info = semantic_cluster_embedding(doc_reps)

    labels = sorted(set(cluster_info.labels))

    # Find the representative document for each cluster
    doc_rep_docs = []

    for label in labels:
        orig_idx = np.where(cluster_info.labels == label)[0]
        sub_vecs = doc_reps[cluster_info.labels == label]

        # Get the cosine similarity between the cluster center and the sub vectors
        sims = cosine_similarity(cluster_info.cluster_centers[label].reshape(1, -1), sub_vecs)

        # Get the original index
        idx = orig_idx[np.argmax(sims)]

        # Append the representative document
        doc_rep_docs.append(split_docs[idx])

    return doc_rep_docs


def tika_parse_pdf(file_path: str) -> list[dict]:
    """
    Parse the PDF file and return the parsed content per page using Apache Tika.

    # https://github.com/chrismattmann/tika-python/issues/191#issuecomment-552593722
    """
    _buffer = StringIO()
    file_data = []

    data = parser.from_file(file_path, xmlContent=True)
    xhtml_data = BeautifulSoup(data["content"])

    for page, content in enumerate(xhtml_data.find_all("div", attrs={"class": "page"})):
        print(f"Parsing page {page+1} of pdf file...")
        _buffer.write(str(content))

        parsed_content = parser.from_buffer(_buffer.getvalue())

        _buffer.seek(0)
        _buffer.truncate()
        file_data.append({"id": "page_" + str(page + 1), "content": parsed_content["content"]})

    return file_data
