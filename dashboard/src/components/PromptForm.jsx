import { useState } from "react";

const CONTENT_TYPES = [
  "cinematic",
  "anime",
  "cartoon",
  "3d_animation",
  "realistic",
  "documentary",
];
const FORMATS = ["reel", "short", "long_video"];
const VIEWS = ["portrait", "landscape", "square"];
const DETAIL = ["medium", "high", "very_high"];

export default function PromptForm({ onStarted, busy }) {
  const [form, setForm] = useState({
    prompt:
      "A little robot finds a dying flower in a deserted city and tries to bring it back to life.",
    contentType: "cinematic",
    contentFormat: "reel",
    viewType: "portrait",
    videoLength: 30,
    onePromptLength: 6,
    detailLevel: "very_high",
    refine: true,
    maxIterations: 3,
    acceptScore: 85,
  });

  const set = (k) => (e) => {
    const v =
      e.target.type === "checkbox"
        ? e.target.checked
        : e.target.type === "number"
        ? Number(e.target.value)
        : e.target.value;
    setForm((f) => ({ ...f, [k]: v }));
  };

  const submit = (e) => {
    e.preventDefault();
    if (!form.prompt.trim()) return;
    onStarted(form);
  };

  return (
    <form className="panel" onSubmit={submit}>
      <h2>New Script</h2>

      <label>Prompt / idea</label>
      <textarea
        value={form.prompt}
        onChange={set("prompt")}
        placeholder="Describe your video idea..."
      />

      <div className="row">
        <div>
          <label>Video type</label>
          <select value={form.contentType} onChange={set("contentType")}>
            {CONTENT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Format</label>
          <select value={form.contentFormat} onChange={set("contentFormat")}>
            {FORMATS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="row">
        <div>
          <label>Aspect</label>
          <select value={form.viewType} onChange={set("viewType")}>
            {VIEWS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Detail level</label>
          <select value={form.detailLevel} onChange={set("detailLevel")}>
            {DETAIL.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="row">
        <div>
          <label>Total length (s)</label>
          <input
            type="number"
            min="1"
            value={form.videoLength}
            onChange={set("videoLength")}
          />
        </div>
        <div>
          <label>Clip length (s)</label>
          <input
            type="number"
            min="1"
            value={form.onePromptLength}
            onChange={set("onePromptLength")}
          />
        </div>
      </div>

      <div className="row">
        <div>
          <label>Max refine loops</label>
          <input
            type="number"
            min="1"
            max="10"
            value={form.maxIterations}
            onChange={set("maxIterations")}
          />
        </div>
        <div>
          <label>Accept score</label>
          <input
            type="number"
            min="0"
            max="100"
            value={form.acceptScore}
            onChange={set("acceptScore")}
          />
        </div>
      </div>

      <label style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 16 }}>
        <input
          type="checkbox"
          style={{ width: "auto" }}
          checked={form.refine}
          onChange={set("refine")}
        />
        Self-critique &amp; refine loop
      </label>

      <button className="btn" type="submit" disabled={busy}>
        {busy ? "Generating…" : "Generate script"}
      </button>
    </form>
  );
}
