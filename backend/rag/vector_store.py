"""ChromaDB vector store management."""

from typing import List, Optional

import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema import Document

from backend.config import CHROMA_PERSIST_DIR, OLLAMA_BASE_URL, EMBEDDING_MODEL


def get_embedding_function():
    """Create the Ollama embedding function."""
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )


def get_vector_store() -> Chroma:
    """Get or create the ChromaDB vector store."""
    return Chroma(
        collection_name="rag_documents",
        embedding_function=get_embedding_function(),
        persist_directory=CHROMA_PERSIST_DIR,
    )


def add_documents(documents: List[Document]) -> None:
    """Add documents to the vector store."""
    store = get_vector_store()
    store.add_documents(documents)


def similarity_search(query: str, k: int = 4) -> List[Document]:
    """Search for similar documents."""
    store = get_vector_store()
    return store.similarity_search(query, k=k)


def get_document_count() -> int:
    """Return the number of documents in the store."""
    store = get_vector_store()
    collection = store._collection
    return collection.count()


def clear_vector_store() -> None:
    """Delete all documents from the vector store."""
    client = chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )
    try:
        client.delete_collection("rag_documents")
    except ValueError:
        pass  # Collection doesn't exist
