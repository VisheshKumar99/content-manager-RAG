function Clip({ clip }) {
  return (
    <div className="clip">
      <h4>
        <span>Clip {clip.clipNumber}</span>
        <span className="badge">{clip.durationSeconds}s</span>
      </h4>
      <div className="fields">
        <div>
          <span className="k">Shot: </span>
          {clip.shotType}
        </div>
        <div>
          <span className="k">Angle: </span>
          {clip.cameraAngle}
        </div>
        <div>
          <span className="k">Movement: </span>
          {clip.cameraMovement}
        </div>
        <div>
          <span className="k">Lighting: </span>
          {clip.lighting}
        </div>
        <div>
          <span className="k">Emotion: </span>
          {clip.facialEmotion}
        </div>
        <div>
          <span className="k">Framing: </span>
          {clip.composition}
        </div>
        <div>
          <span className="k">Mood: </span>
          {clip.mood}
        </div>
        <div>
          <span className="k">Audio: </span>
          {clip.audioPrompt}
        </div>
      </div>
      {clip.videoPrompt && <div className="vp">{clip.videoPrompt}</div>}
    </div>
  );
}

export default function PlanView({ plan }) {
  if (!plan) return null;
  return (
    <div>
      {plan.story && (
        <>
          <div className="section-label">Story</div>
          <div className="story">{plan.story}</div>
        </>
      )}

      {Array.isArray(plan.characters) && plan.characters.length > 0 && (
        <>
          <div className="section-label">Characters</div>
          {plan.characters.map((c) => (
            <div className="clip" key={c.characterId || c.name}>
              <h4>{c.name}</h4>
              <div className="vp">{c.designPrompt}</div>
            </div>
          ))}
        </>
      )}

      {Array.isArray(plan.environments) && plan.environments.length > 0 && (
        <>
          <div className="section-label">Environments</div>
          {plan.environments.map((env) => (
            <div className="clip" key={env.environmentId || env.name}>
              <h4>{env.name}</h4>
              <div className="vp">{env.designPrompt}</div>
            </div>
          ))}
        </>
      )}

      {Array.isArray(plan.clips) && plan.clips.length > 0 && (
        <>
          <div className="section-label">Clips</div>
          {plan.clips.map((c) => (
            <Clip key={c.clipNumber} clip={c} />
          ))}
        </>
      )}
    </div>
  );
}
