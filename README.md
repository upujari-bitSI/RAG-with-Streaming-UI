# RAG with Streaming UI

A ChatGPT-like interactive chatbot that runs entirely on your local machine using a local LLM (via Ollama) and your own uploaded documents.

## Features

- **Local LLM** — Uses Ollama to run models like Mistral, Llama, etc. locally
- **Document Upload** — Upload PDF, TXT, MD, or DOCX files to build a knowledge base
- **RAG Pipeline** — Retrieval-Augmented Generation using ChromaDB for vector storage
- **Streaming UI** — Real-time token-by-token response streaming (ChatGPT-style)
- **No external APIs** — Everything runs on your machine, your data stays private

## Architecture

```
Frontend (HTML/CSS/JS)
    ↓ SSE streaming
FastAPI Backend
    ├── /api/chat/stream  → LLM streaming via Ollama
    ├── /api/upload       → Document ingestion
    └── /api/status       → Knowledge base status
        ↓
RAG Pipeline (LangChain)
    ├── Document Loader (PDF, TXT, MD, DOCX)
    ├── Text Splitter (recursive chunking)
    ├── Embeddings (Ollama nomic-embed-text)
    └── Vector Store (ChromaDB)
```

## Prerequisites

1. **Python 3.10+**
2. **Ollama** — Install from [ollama.com](https://ollama.com)
3. Pull the required models:
   ```bash
   ollama pull mistral
   ollama pull nomic-embed-text
   ```

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd RAG-with-Streaming-UI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Start the server
python -m backend.main
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Usage

1. **Upload documents** using the sidebar to build your knowledge base
2. **Ask questions** in the chat — the bot retrieves relevant context from your documents
3. If no documents are uploaded, the bot works as a regular chat assistant

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/stream` | Streaming chat (SSE) |
| POST | `/api/chat` | Non-streaming chat |
| POST | `/api/upload` | Upload a document |
| GET | `/api/status` | Knowledge base status |
| DELETE | `/api/documents` | Clear all documents |

## Configuration

Edit `.env` to customize:

- `LLM_MODEL` — Ollama model name (default: `mistral`)
- `EMBEDDING_MODEL` — Embedding model (default: `nomic-embed-text`)
- `CHUNK_SIZE` / `CHUNK_OVERLAP` — Document chunking parameters
- `RETRIEVAL_TOP_K` — Number of context chunks to retrieve
