"""Run endpoints: start a refinement run, list/get runs, and stream
live iteration events over Server-Sent Events (SSE).

A run executes the generate -> critique -> refine loop in a background
thread. Each phase event is (a) persisted to SQLite and (b) pushed to
any connected SSE listeners for that run via an in-memory broker.
"""

from __future__ import annotations

import json
import queue
import threading
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app import db
from rag.prompt_pipeline.prompt_builder import promptRectifyPipeline
from rag.prompt_pipeline.schemas import VideoConfig

router = APIRouter(prefix="/runs", tags=["runs"])


class _Broker:
    """Fan-out of live run events to connected SSE subscribers.

    Each run id maps to a set of per-subscriber queues. Publishing an
    event copies it into every subscriber queue. A sentinel (None)
    signals end-of-stream.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subscribers: dict[str, set[queue.Queue]] = {}

    def subscribe(self, run_id: str) -> "queue.Queue":
        q: queue.Queue = queue.Queue()
        with self._lock:
            self._subscribers.setdefault(run_id, set()).add(q)
        return q

    def unsubscribe(self, run_id: str, q: "queue.Queue") -> None:
        with self._lock:
            subs = self._subscribers.get(run_id)
            if subs and q in subs:
                subs.discard(q)
                if not subs:
                    self._subscribers.pop(run_id, None)

    def publish(self, run_id: str, event: dict | None) -> None:
        with self._lock:
            subs = list(self._subscribers.get(run_id, set()))
        for q in subs:
            q.put(event)


broker = _Broker()


class StartRunRequest(BaseModel):
    prompt: str
    contentType: str = "cinematic"
    contentFormat: str = "reel"
    viewType: str = "portrait"
    videoLength: int = 30
    onePromptLength: int = 6
    detailLevel: str = "very_high"
    refine: bool = True
    maxIterations: int = 3
    acceptScore: int = 85


class StartRunResponse(BaseModel):
    runId: str


def _execute_run(run_id: str, prompt: str, config: VideoConfig) -> None:
    """Background worker: run the loop, persist + broadcast each event."""

    def on_event(event: dict) -> None:
        db.add_iteration(run_id, event)
        # Keep the SSE payload light: drop the full plan from the stream
        # frame (the client can fetch the plan via the run endpoint or
        # from the "final" frame which includes it).
        broker.publish(run_id, event)

    try:
        final_plan = promptRectifyPipeline(prompt, config, on_event=on_event)
        # Compute best score from the persisted run.
        run = db.get_run(run_id)
        best = None
        if run:
            scores = [
                it["score"]
                for it in run.get("iterations", [])
                if it["score"] is not None
            ]
            best = max(scores) if scores else None
        db.finish_run(
            run_id,
            status="done",
            best_score=best,
            final_plan=final_plan,
        )
        broker.publish(
            run_id,
            {"phase": "done", "message": "Run complete.", "plan": final_plan},
        )
    except Exception as exc:  # noqa: BLE001 - surface any failure to UI
        db.finish_run(run_id, status="failed", error=str(exc))
        broker.publish(
            run_id,
            {"phase": "error", "message": f"Run failed: {exc}"},
        )
    finally:
        broker.publish(run_id, None)  # end-of-stream sentinel


@router.post("", response_model=StartRunResponse)
def start_run(request: StartRunRequest) -> StartRunResponse:
    run_id = uuid.uuid4().hex

    try:
        config = VideoConfig(
            contentType=request.contentType,
            contentFormat=request.contentFormat,
            viewType=request.viewType,
            videoLength=request.videoLength,
            onePromptLength=request.onePromptLength,
            detailLevel=request.detailLevel,
            refine=request.refine,
            maxIterations=request.maxIterations,
            acceptScore=request.acceptScore,
        )
    except Exception as exc:  # pydantic validation errors
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    db.create_run(run_id, request.prompt, config.model_dump())

    thread = threading.Thread(
        target=_execute_run,
        args=(run_id, request.prompt, config),
        daemon=True,
    )
    thread.start()

    return StartRunResponse(runId=run_id)


@router.get("")
def get_runs() -> list[dict]:
    return db.list_runs()


@router.get("/{run_id}")
def get_run(run_id: str) -> dict:
    run = db.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/stream")
def stream_run(run_id: str) -> StreamingResponse:
    run = db.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    def event_gen():
        q = broker.subscribe(run_id)
        try:
            # Replay what already happened so late subscribers catch up.
            for it in run.get("iterations", []):
                yield f"data: {json.dumps(it)}\n\n"

            # If the run already finished, close immediately.
            if run["status"] in ("done", "failed"):
                yield "event: end\ndata: {}\n\n"
                return

            while True:
                event = q.get()
                if event is None:  # sentinel: run finished
                    yield "event: end\ndata: {}\n\n"
                    return
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            broker.unsubscribe(run_id, q)

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
