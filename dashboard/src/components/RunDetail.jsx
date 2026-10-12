import { useEffect, useRef, useState } from "react";
import { getRun, streamRun } from "../api";
import PlanView from "./PlanView";

// Shows one run: a live timeline of generate/critique/refine events plus
// the latest plan. Subscribes to SSE while the run is active.
export default function RunDetail({ runId, onRunUpdated }) {
  const [events, setEvents] = useState([]);
  const [plan, setPlan] = useState(null);
  const [status, setStatus] = useState("running");
  const esRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    setEvents([]);
    setPlan(null);
    setStatus("running");

    // Load persisted state first, then open the live stream.
    getRun(runId).then((run) => {
      if (cancelled || !run) return;
      setStatus(run.status);
      if (run.finalPlan) setPlan(run.finalPlan);
    });

    const es = streamRun(
      runId,
      (ev) => {
        if (cancelled) return;
        setEvents((prev) => [...prev, ev]);
        if (ev.plan) setPlan(ev.plan);
        if (ev.phase === "done") setStatus("done");
        if (ev.phase === "error") setStatus("failed");
      },
      () => {
        if (cancelled) return;
        // Refresh persisted run to capture final status/score/plan.
        getRun(runId).then((run) => {
          if (cancelled || !run) return;
          setStatus(run.status);
          if (run.finalPlan) setPlan(run.finalPlan);
          onRunUpdated && onRunUpdated();
        });
      }
    );
    esRef.current = es;

    return () => {
      cancelled = true;
      es.close();
    };
  }, [runId]);

  return (
    <div className="panel">
      <div className="runs-head">
        <h2 style={{ margin: 0 }}>
          Live progress{" "}
          {status === "running" && <span className="spinner" />}
        </h2>
        <span className={`badge ${status}`}>{status}</span>
      </div>

      <div className="timeline">
        {events.length === 0 && status === "running" && (
          <div className="step">
            <span className="dot" />
            <div className="msg">
              Starting… <span className="spinner" />
            </div>
          </div>
        )}
        {events.map((ev, i) => (
          <div className="step" key={i}>
            <span className="dot" />
            <div className="phase">
              {ev.phase}
              {typeof ev.score === "number" ? ` · score ${ev.score}` : ""}
              {ev.iteration ? ` · #${ev.iteration}` : ""}
            </div>
            <div className="msg">{ev.message}</div>
          </div>
        ))}
      </div>

      {plan && (
        <div style={{ marginTop: 18 }}>
          <PlanView plan={plan} />
        </div>
      )}
    </div>
  );
}
