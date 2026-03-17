"""API route definitions."""

import os
import json
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from backend.config import UPLOAD_DIR
from backend.api.models import ChatRequest, ChatResponse, UploadResponse, StoreStatus
from backend.rag.document_loader import ingest_file, get_supported_extensions
from backend.rag.vector_store import (
    add_documents,
    get_document_count,
    clear_vector_store,
)
from backend.rag.chain import stream_answer, get_answer

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    """Non-streaming chat endpoint."""
    answer = get_answer(request.question)
    return ChatResponse(
        answer=answer,
        sources_used=get_document_count() > 0,
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint using Server-Sent Events."""

    async def event_generator():
        try:
            async for token in stream_answer(request.question):
                data = json.dumps({"token": token})
                yield f"data: {data}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and ingest a document into the vector store."""
    ext = os.path.splitext(file.filename)[1].lower()
    supported = get_supported_extensions()
    if ext not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {supported}",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        chunks = ingest_file(file_path)
        add_documents(chunks)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")

    return UploadResponse(
        filename=file.filename,
        chunks=len(chunks),
        message=f"Successfully ingested {len(chunks)} chunks from {file.filename}",
    )


@router.get("/status", response_model=StoreStatus)
async def get_status():
    """Get the current status of the vector store."""
    return StoreStatus(
        document_chunks=get_document_count(),
        supported_extensions=get_supported_extensions(),
    )


@router.delete("/documents")
async def delete_documents():
    """Clear all documents from the vector store."""
    clear_vector_store()
    return {"message": "All documents have been cleared from the vector store."}
