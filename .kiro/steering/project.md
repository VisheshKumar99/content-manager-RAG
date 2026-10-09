# Project: content-manager-RAG

> This is a steering file. Kiro loads it automatically as context on relevant
> queries, so you don't have to re-explain the project each time. Keep it short
> and current — stale or bloated steering wastes tokens instead of saving them.

## What this project is

A content manager built on a RAG (Retrieval-Augmented Generation) pipeline.
A Next.js dashboard talks to a FastAPI server, which runs a RAG system whose
agent retrieves context and answers via OpenAI.

Request flow: Next.js UI → FastAPI route (`app/`) → RAG system (`rag/`) → agent → OpenAI.

## Tech stack

- Frontend: Next.js (in `dashboard/`)
- Backend: FastAPI + Uvicorn (Python, in `server/`)
- LLM / embeddings: OpenAI (`openai`)
- Config: environment variables via `python-dotenv` (`server/.env`)
<!-- Add: vector store (Chroma/FAISS/pgvector), DB, etc. as you add them. -->

## Project structure

```
content-manager-RAG/
├── dashboard/          # Next.js frontend (UI)
├── docs/               # personal reference notes (NOT auto-loaded by Kiro)
└── server/             # Python backend
    ├── .env            # secrets (gitignored)
    ├── requirements.txt
    ├── app/            # FastAPI layer
    │   ├── main.py     # app entry point + CORS + /health
    │   └── routes/     # API endpoints (e.g. chat.py)
    └── rag/            # RAG system
        ├── agent.py        # the agent (retrieve + answer)
        ├── retriever.py    # retrieval (placeholder vector store)
        ├── embeddings.py   # embedding helpers
        └── store/          # vector store data
```

## Conventions

- Backend commands run from `server/`.
- Install deps: `pip3 install -r requirements.txt`
- Run API: `uvicorn app.main:app --reload`
- Secrets live in `server/.env` (never commit; see `server/.env.example`).

## Notes for Kiro

<!-- Anything you'd otherwise repeat every chat. Example:
     "Always use type hints." "Prefer async." "The RAG store is Chroma." -->
- `app/` (FastAPI) depends on `rag/`; keep `rag/` free of web-framework code.
