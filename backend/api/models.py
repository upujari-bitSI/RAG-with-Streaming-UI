"""Pydantic request/response models."""

from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources_used: bool


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str


class StoreStatus(BaseModel):
    document_chunks: int
    supported_extensions: List[str]
