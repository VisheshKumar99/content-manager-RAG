function fmtTime(iso) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function RunList({ runs, selectedId, onSelect }) {
  if (!runs.length) {
    return <div className="empty">No scripts yet. Generate one to begin.</div>;
  }
  return (
    <div>
      {runs.map((run) => (
        <div
          key={run.id}
          className={`run-card ${run.id === selectedId ? "active" : ""}`}
          onClick={() => onSelect(run.id)}
        >
          <div className="prompt">{run.prompt}</div>
          <div className="meta">
            <span className={`badge ${run.status}`}>{run.status}</span>
            <span className="badge">{run.config?.contentType}</span>
            <span className="badge">{run.config?.videoLength}s</span>
            {typeof run.bestScore === "number" && (
              <span className="score-pill">★ {run.bestScore}</span>
            )}
            <span className="badge" style={{ border: "none" }}>
              {fmtTime(run.createdAt)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
