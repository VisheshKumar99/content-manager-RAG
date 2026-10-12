// All calls go through the Vite dev proxy at /api -> FastAPI :8000.
const BASE = "/api";

export async function startRun(payload) {
  const res = await fetch(`${BASE}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Failed to start run: ${detail}`);
  }
  return res.json(); // { runId }
}

export async function listRuns() {
  const res = await fetch(`${BASE}/runs`);
  if (!res.ok) throw new Error("Failed to load runs");
  return res.json();
}

export async function getRun(runId) {
  const res = await fetch(`${BASE}/runs/${runId}`);
  if (!res.ok) throw new Error("Failed to load run");
  return res.json();
}

// Open an SSE stream for a run. onEvent(event) fires per iteration,
// onEnd() fires when the stream closes. Returns the EventSource so the
// caller can close it.
export function streamRun(runId, onEvent, onEnd) {
  const es = new EventSource(`${BASE}/runs/${runId}/stream`);
  es.onmessage = (e) => {
    try {
      onEvent(JSON.parse(e.data));
    } catch {
      /* ignore malformed frames */
    }
  };
  es.addEventListener("end", () => {
    es.close();
    onEnd && onEnd();
  });
  es.onerror = () => {
    es.close();
    onEnd && onEnd();
  };
  return es;
}
