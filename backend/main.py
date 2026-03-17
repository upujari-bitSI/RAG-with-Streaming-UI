"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router
from backend.config import HOST, PORT, UPLOAD_DIR

app = FastAPI(
    title="RAG Chatbot",
    description="Local RAG-powered chatbot with streaming UI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


def main():
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    main()
