# Script Studio — Dashboard

Dark-themed React (Vite) UI for the content-manager-RAG video script
pipeline. You enter a prompt plus choices (video type, duration, style,
refine loops); the backend runs the generate → critique → refine loop,
saves every iteration to SQLite, and streams live progress here.

## Run it

Two processes, in two terminals.

**1. Backend (FastAPI, port 8000)** — from `server/`:

```bash
pip3 install -r requirements.txt
uvicorn app.main:app --reload
```

**2. Frontend (Vite, port 5173)** — from `dashboard/`:

```bash
npm install
npm run dev
```

Open http://localhost:5173.

## How it works

- The UI calls the API through the Vite proxy at `/api` → `http://localhost:8000`.
- `POST /runs` starts a run in a background thread and returns a `runId`.
- The run detail view opens an SSE stream at `/api/runs/{id}/stream` and
  shows each generate/critique/refine step as it happens, plus the latest plan.
- Runs and iterations persist in `server/data/app.db` (SQLite), so the
  script list and history survive restarts.

## Note on model

With the default local Ollama model (`qwen2.5:3b`) a run takes a few
minutes and quality is modest. Set `LLM_PROVIDER=openai` with an
`OPENAI_API_KEY` in `server/.env`, or lower `maxIterations`, for faster
and better results.
