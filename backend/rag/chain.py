"""RAG chain: retrieval + LLM generation with streaming."""

from typing import AsyncGenerator

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.callbacks import AsyncIteratorCallbackHandler

from backend.config import OLLAMA_BASE_URL, LLM_MODEL, RETRIEVAL_TOP_K
from backend.rag.vector_store import similarity_search, get_document_count

RAG_PROMPT_TEMPLATE = """\
You are a helpful assistant. Use the following retrieved context to answer the user's question.
If the context does not contain enough information, say so honestly — do not make up facts.

Context:
{context}

Question: {question}

Answer:"""

STANDALONE_PROMPT_TEMPLATE = """\
You are a helpful assistant. Answer the user's question to the best of your ability.

Question: {question}

Answer:"""


def _build_prompt(question: str, context: str | None) -> str:
    if context:
        return RAG_PROMPT_TEMPLATE.format(context=context, question=question)
    return STANDALONE_PROMPT_TEMPLATE.format(question=question)


def _retrieve_context(question: str) -> str | None:
    """Retrieve relevant context from the vector store."""
    if get_document_count() == 0:
        return None
    docs = similarity_search(question, k=RETRIEVAL_TOP_K)
    if not docs:
        return None
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


async def stream_answer(question: str) -> AsyncGenerator[str, None]:
    """Stream the LLM response token-by-token."""
    import asyncio

    context = _retrieve_context(question)
    prompt = _build_prompt(question, context)

    callback = AsyncIteratorCallbackHandler()

    llm = Ollama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        callbacks=[callback],
        temperature=0.3,
    )

    task = asyncio.create_task(llm.ainvoke(prompt))

    async for token in callback.aiter():
        yield token

    await task


def get_answer(question: str) -> str:
    """Get a non-streaming answer (for testing / fallback)."""
    context = _retrieve_context(question)
    prompt = _build_prompt(question, context)

    llm = Ollama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
    )
    return llm.invoke(prompt)
