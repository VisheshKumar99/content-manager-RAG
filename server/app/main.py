"""FastAPI entry point for the content-manager-RAG server."""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import db
from app.routes import runs

load_dotenv()

app = FastAPI(title="content-manager-RAG API")

# Allow the dashboard (Next.js :3000 or Vite :5173) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


app.include_router(runs.router)

# The chat router depends on OpenAI being configured (it builds the RAG
# agent/embeddings at import time). Load it only if that import succeeds,
# so an Ollama-only setup without OPENAI_API_KEY still boots the API.
try:
    from app.routes import chat

    app.include_router(chat.router)
except Exception as exc:  # noqa: BLE001
    print(f"[startup] chat router disabled: {exc}")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
