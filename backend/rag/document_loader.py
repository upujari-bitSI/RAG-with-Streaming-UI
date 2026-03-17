"""Document loading and chunking utilities."""

import os
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain.schema import Document

from backend.config import CHUNK_SIZE, CHUNK_OVERLAP, UPLOAD_DIR

# Supported file extensions and their loaders
LOADER_MAP = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".md": TextLoader,
    ".docx": Docx2txtLoader,
}


def get_supported_extensions() -> List[str]:
    return list(LOADER_MAP.keys())


def load_document(file_path: str) -> List[Document]:
    """Load a single document based on its file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    loader_cls = LOADER_MAP.get(ext)
    if loader_cls is None:
        raise ValueError(
            f"Unsupported file type: {ext}. "
            f"Supported: {get_supported_extensions()}"
        )
    loader = loader_cls(file_path)
    return loader.load()


def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def ingest_file(file_path: str) -> List[Document]:
    """Load a file and split it into chunks ready for embedding."""
    docs = load_document(file_path)
    return split_documents(docs)
