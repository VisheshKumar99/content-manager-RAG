import { useCallback, useEffect, useState } from "react";
import { listRuns, startRun } from "./api";
import PromptForm from "./components/PromptForm";
import RunList from "./components/RunList";
import RunDetail from "./components/RunDetail";

export default function App() {
  const [runs, setRuns] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const refreshRuns = useCallback(async () => {
    try {
      const data = await listRuns();
      setRuns(data);
      return data;
    } catch (e) {
      setError(e.message);
      return [];
    }
  }, []);

  useEffect(() => {
    refreshRuns();
  }, [refreshRuns]);

  // Poll the list while any run is active so statuses/scores update.
  useEffect(() => {
    const hasRunning = runs.some((r) => r.status === "running");
    if (!hasRunning) return;
    const id = setInterval(refreshRuns, 4000);
    return () => clearInterval(id);
  }, [runs, refreshRuns]);

  const handleStart = async (form) => {
    setBusy(true);
    setError(null);
    try {
      const { runId } = await startRun(form);
      await refreshRuns();
      setSelectedId(runId);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app">
      <div className="topbar">
        <div className="logo" />
        <div>
          <div className="title">Script Studio</div>
          <div className="subtitle">
            AI video director · prompt → critique → refine
          </div>
        </div>
      </div>

      {error && (
        <div
          className="panel"
          style={{ borderColor: "rgba(248,113,113,.4)", marginBottom: 18 }}
        >
          <span style={{ color: "var(--bad)" }}>{error}</span>
        </div>
      )}

      <div className="grid">
        <div>
          <PromptForm onStarted={handleStart} busy={busy} />
          <div className="panel" style={{ marginTop: 18 }}>
            <div className="runs-head">
              <h2 style={{ margin: 0 }}>Scripts</h2>
              <span className="badge">{runs.length}</span>
            </div>
            <RunList
              runs={runs}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          </div>
        </div>

        <div>
          {selectedId ? (
            <RunDetail
              key={selectedId}
              runId={selectedId}
              onRunUpdated={refreshRuns}
            />
          ) : (
            <div className="panel">
              <div className="empty">
                Select a script on the left, or generate a new one to watch it
                build in real time.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
