import json

from rag.llm.factory import get_llm
from rag.prompt_pipeline.schemas import VideoConfig

llm = get_llm()


# Required cinematography / direction fields every clip must specify.
CLIP_REQUIRED_FIELDS = [
    "shotType",
    "cameraAngle",
    "cameraMovement",
    "lighting",
    "facialEmotion",
    "composition",
    "action",
    "mood",
    "videoPrompt",
    "audioPrompt",
]


# Style-specific visual direction. The pipeline injects the block that
# matches config.contentType so the plan uses the right visual language.
STYLE_GUIDES = {
    "cinematic": """
STYLE: CINEMATIC (live-action film look)
- Treat it like a real film shoot: lenses, depth of field, film grain,
  anamorphic flares, naturalistic physics and skin.
- Lighting: motivated, directional light (key/fill/back), practical
  sources, soft or hard shadows, color temperature, time of day.
- Camera: real rig language, dolly, crane, handheld, steadicam,
  tracking, rack focus; specify lens feel (wide 24mm vs 85mm portrait).
- Facial emotion must read through subtle, human micro-expressions.
""",
    "anime": """
STYLE: ANIME (Japanese 2D animation)
- Cel-shaded 2D, clean line art, flat color fills with gradient
  shadows, expressive large eyes, speed lines and impact frames for
  action, dramatic sakuga moments.
- Lighting: stylized rim light, bloom, lens flares, god rays, strong
  color grading (sunset oranges, cool night blues).
- Camera: dynamic 2D camera moves, dramatic angles, speed-line pans,
  dutch tilts, zoom punches on emotion.
- Facial emotion is exaggerated and iconographic (sweat drops, blush,
  wide eyes, shadowed eyes for dread).
""",
    "cartoon": """
STYLE: CARTOON (Western toon / stylized 2D)
- Bold outlines, bright saturated flat colors, squash-and-stretch,
  rubber-hose or chunky shapes, playful exaggeration.
- Lighting: simple, flat, high-key and cheerful; minimal realistic
  shadowing.
- Camera: snappy, bouncy framing, quick cuts, exaggerated zooms.
- Facial emotion is big and broad; eyes and mouth do the acting.
""",
    "3d_animation": """
STYLE: 3D ANIMATION (Pixar/DreamWorks-style CGI)
- Stylized but volumetric 3D forms, subsurface skin, soft global
  illumination, appealing character proportions.
- Lighting: cinematic three-point plus bounce, ambient occlusion,
  warm/cool contrast, polished render.
- Camera: virtual cinematography, smooth dolly and crane moves,
  shallow depth of field for emphasis.
- Facial emotion through a detailed rig: brows, eye darts, mouth shapes.
""",
    "realistic": """
STYLE: REALISTIC (photoreal, documentary-grade)
- Photographic realism, accurate materials, natural light physics,
  no stylization.
- Lighting: real-world available light, correct shadows and bounce.
- Camera: believable handheld or tripod framing, real lens behavior.
- Facial emotion is restrained and authentic.
""",
    "documentary": """
STYLE: DOCUMENTARY (observational, grounded)
- Naturalistic, candid, grounded framing; avoid over-stylization.
- Lighting: available/natural light, practical sources.
- Camera: observational handheld, slow push-ins, interview framing.
- Facial emotion is genuine and understated.
""",
}


def _style_guide(content_type: str) -> str:
    return STYLE_GUIDES.get(content_type, STYLE_GUIDES["cinematic"]).strip()


SYSTEM_PROMPT = """
You are a specialist film DIRECTOR and SCRIPT ANALYST working as a
cinematographer, character designer, lighting designer, and AI video
prompt engineer at the same time.

Your job is to turn a raw idea into a production-ready, shot-by-shot
AI video plan where EVERY creative decision is explicit. Nothing may
be left vague. A junior artist must be able to render each clip from
your plan alone, with no guessing.

Adopt the requested STYLE below and apply its visual language to every
character, environment, and clip. The same story looks completely
different in anime vs cartoon vs cinematic, and your plan must reflect
that difference in line work, shading, lighting, camera, and emotion.

{style_guide}

MANDATORY DIRECTION RULES:

1. STORY AND HOOK
- Strong hook in the FIRST clip (the first ~2 seconds must grab
  attention).
- Clear progression: setup, rising tension/curiosity, turn, payoff.
- Every clip advances the story; no filler, no near-duplicate clips.
- End on a satisfying or surprising beat.

2. CHARACTERS
- One reference per unique character with a stable characterId.
- Specify age, proportions, face, eyes, hair, clothing, colors,
  accessories, personality, and distinguishing features, drawn in the
  requested STYLE.
- Keep appearance identical across every clip.

3. ENVIRONMENTS
- Reusable reference per location with a stable environmentId.
- Specify layout, materials, colors, atmosphere, weather, time of day,
  and base lighting, in the requested STYLE.

4. EVERY CLIP MUST SPECIFY, EXPLICITLY (never vague words like "nice"):
- shotType: extreme close-up, close-up, medium, wide, extreme wide,
  over-the-shoulder, POV, two-shot, or insert/macro.
- cameraAngle: eye-level, low angle, high angle, dutch tilt,
  bird's-eye, or worm's-eye.
- cameraMovement: static, slow push-in, pull-out, pan L/R, tilt,
  tracking, dolly, crane, handheld, orbit, whip pan, or zoom punch.
- lighting: key direction and quality, color temperature, contrast,
  practical sources, mood (e.g. "hard low-key rim light, cold blue").
- facialEmotion: the lead's readable expression and micro-expression
  for this exact moment (e.g. "wide-eyed hope softening to relief").
- composition: framing, subject placement, rule-of-thirds or centered,
  foreground/background layering, headroom, negative space.
- action: what physically happens during the shot (motion, not a
  static pose).
- mood: emotional tone of the shot.
- videoPrompt: one self-contained paragraph a video model can use
  directly, WEAVING TOGETHER all of the above fields in the STYLE.
- audioPrompt: ambience, sfx, and music tone for the shot.

5. CONTINUITY
- Preserve character appearance, clothing, props, geography, lighting
  continuity, and story state across clips.
- Vary shotType and cameraMovement across clips; never repeat the same
  framing back-to-back.

6. FORMAT
- Respect viewType: portrait = vertical composition, landscape = wide
  cinematic composition, square = centered balanced.
- Fit the action to the clip duration; do not overload a short shot.
- No logos, watermarks, or unintended text.

OUTPUT RULES:
- Return valid JSON ONLY. No Markdown fences, no commentary.
- Do not echo the input request back.
- Use EXACTLY the keys in the OUTPUT SCHEMA. Do not rename, add, or
  omit top-level keys. Every clip field is REQUIRED and non-empty.

OUTPUT SCHEMA (return an object with exactly these top-level keys):
{{
  "story": "string",
  "styleNotes": "string (how the chosen STYLE is applied overall)",
  "characters": [
    {{
      "characterId": "string",
      "name": "string",
      "designPrompt": "string"
    }}
  ],
  "environments": [
    {{
      "environmentId": "string",
      "name": "string",
      "designPrompt": "string"
    }}
  ],
  "clips": [
    {{
      "clipNumber": 1,
      "durationSeconds": 6,
      "shotType": "string",
      "cameraAngle": "string",
      "cameraMovement": "string",
      "lighting": "string",
      "facialEmotion": "string",
      "composition": "string",
      "action": "string",
      "mood": "string",
      "videoPrompt": "string",
      "audioPrompt": "string"
    }}
  ]
}}

- "clips" MUST contain exactly numberOfClips items.
- Each clip's "durationSeconds" MUST match clipDurationsSeconds for
  that clip, and the clip durations MUST sum to totalDurationSeconds.
- No clip field may be empty or vague.
"""


CRITIC_PROMPT = """
You are a strict specialist film DIRECTOR and SCRIPT ANALYST reviewing
an AI video plan before production. You know the requested STYLE's
visual language and judge the plan harshly against it.

{style_guide}

Review EVERY clip against ALL of these criteria. Be specific and
unforgiving. A real production team must be able to shoot from this
plan with zero guesswork.

1. HOOK AND STORY: strong hook in clip 1; clear setup, rising
   tension/curiosity, turn, and a satisfying payoff; every clip
   advances the story.
2. CLIP VARIETY: no near-duplicate clips; shotType and cameraMovement
   must vary across clips.
3. SHOT CLARITY: each clip states a concrete shotType, cameraAngle,
   and cameraMovement (not vague).
4. LIGHTING: each clip specifies direction, quality, color temperature,
   contrast, and mood appropriate to the STYLE.
5. FACIAL EMOTION: each clip states a readable, specific expression
   that fits the story beat and the STYLE.
6. COMPOSITION: framing, subject placement, and layering are explicit
   and respect the aspect ratio (portrait/landscape/square).
7. STYLE FIDELITY: characters, environments, lighting, and camera all
   match the requested STYLE (anime vs cartoon vs cinematic, etc.).
8. CONTINUITY: appearance, clothing, props, geography, and lighting
   stay consistent across clips.
9. COMPLETENESS: no empty, vague, or missing fields.

Return valid JSON ONLY, with EXACTLY these keys:
{{
  "approved": true,
  "score": 0,
  "issues": [
    {{
      "location": "string (e.g. 'clip 3', 'character Bot', 'story')",
      "criterion": "string (which criterion above failed)",
      "problem": "string",
      "fix": "string (concrete, actionable instruction)"
    }}
  ]
}}

- "score" is an integer 0-100 for overall production readiness.
- Set "approved" to true ONLY when the plan is production-ready with no
  meaningful room for improvement on ANY criterion; otherwise false.
- When approved is true, "issues" MUST be an empty list.
- Do not include Markdown fences or commentary.
"""


def _build_clip_plan(config: VideoConfig) -> dict:
    clip_count = (
        config.videoLength + config.onePromptLength - 1
    ) // config.onePromptLength

    durations = [
        min(
            config.onePromptLength,
            config.videoLength - i * config.onePromptLength,
        )
        for i in range(clip_count)
    ]

    return {
        "numberOfClips": clip_count,
        "clipDurationsSeconds": durations,
        "totalDurationSeconds": config.videoLength,
    }


def _parse_json(response: str, context: str) -> dict:
    try:
        return json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON during {context}. "
            "Retry or repair the response."
        ) from exc


def _validate_plan(result: dict, config: VideoConfig) -> dict:
    clip_plan = _build_clip_plan(config)
    clip_count = clip_plan["numberOfClips"]

    clips = result.get("clips", [])

    if len(clips) != clip_count:
        raise ValueError(
            f"Expected {clip_count} clips, received {len(clips)}"
        )

    actual_duration = sum(
        clip.get("durationSeconds", 0) for clip in clips
    )

    if actual_duration != config.videoLength:
        raise ValueError(
            f"Expected {config.videoLength}s, received {actual_duration}s"
        )

    # Every clip must carry the full set of direction fields, filled in.
    for clip in clips:
        number = clip.get("clipNumber", "?")
        missing = [
            field
            for field in CLIP_REQUIRED_FIELDS
            if not str(clip.get(field, "")).strip()
        ]
        if missing:
            raise ValueError(
                f"Clip {number} is missing or empty fields: "
                f"{', '.join(missing)}"
            )

    return result


def generatePlan(prompt: str, config: VideoConfig) -> dict:
    """Single-pass generation of a video plan from a raw idea."""

    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    user_request = {
        "rawIdea": prompt,
        "configuration": config.model_dump(),
        "clipPlan": _build_clip_plan(config),
        "outputRequirements": {
            "storyline": True,
            "styleNotes": True,
            "characterReferencePrompts": True,
            "environmentReferencePrompts": True,
            "perClipDirection": True,
            "shotTypeAngleMovement": True,
            "lightingStrategy": True,
            "facialEmotion": True,
            "composition": True,
            "audioPrompts": True,
            "returnFormat": "JSON",
        },
    }

    system = SYSTEM_PROMPT.format(style_guide=_style_guide(config.contentType))

    full_prompt = f"""
{system}

Create the video plan for this request:

{json.dumps(user_request, ensure_ascii=False, indent=2)}

Return the complete JSON object.
"""

    response = llm.generate(full_prompt)
    result = _parse_json(response, "generation")
    return _validate_plan(result, config)


def critiquePlan(plan: dict, config: VideoConfig) -> dict:
    """Ask the LLM to review a plan and return a structured verdict."""

    review_request = {
        "configuration": config.model_dump(),
        "clipPlan": _build_clip_plan(config),
        "planUnderReview": plan,
    }

    critic = CRITIC_PROMPT.format(style_guide=_style_guide(config.contentType))

    full_prompt = f"""
{critic}

Review this video plan:

{json.dumps(review_request, ensure_ascii=False, indent=2)}

Return the verdict JSON object.
"""

    response = llm.generate(full_prompt)
    verdict = _parse_json(response, "critique")

    verdict.setdefault("approved", False)
    verdict.setdefault("issues", [])
    return verdict


def refinePlan(plan: dict, verdict: dict, config: VideoConfig) -> dict:
    """Produce an improved plan that addresses the critique's issues."""

    refine_request = {
        "configuration": config.model_dump(),
        "clipPlan": _build_clip_plan(config),
        "currentPlan": plan,
        "reviewerIssues": verdict.get("issues", []),
    }

    system = SYSTEM_PROMPT.format(style_guide=_style_guide(config.contentType))

    full_prompt = f"""
{system}

A reviewer found problems in the current plan. Produce an IMPROVED
plan that fixes EVERY listed issue while keeping everything that was
already good. Keep the same characters and environments unless an
issue requires changing them. Keep the chosen STYLE consistent.

{json.dumps(refine_request, ensure_ascii=False, indent=2)}

Return the complete improved JSON object using the OUTPUT SCHEMA.
"""

    response = llm.generate(full_prompt)
    result = _parse_json(response, "refinement")
    return _validate_plan(result, config)


def _noop(_event: dict) -> None:
    """Default progress callback that does nothing."""


def promptRectifyPipeline(prompt: str, config: VideoConfig, on_event=None) -> dict:
    """Generate a plan, then iteratively self-critique and refine it
    until the LLM approves it or maxIterations is reached.

    on_event(event: dict) is called at each phase so callers (e.g. the
    API layer) can persist and stream progress. Event shape:
        {
          "phase": "generate" | "critique" | "refine" | "final",
          "iteration": int,          # 0 for generate, N for loop steps
          "plan": dict | None,       # current plan after this phase
          "score": int | None,       # critique score (critique/final)
          "approved": bool | None,   # critique verdict
          "issues": list,            # critique issues
          "message": str,            # human-readable status
        }
    """

    emit = on_event or _noop

    plan = generatePlan(prompt, config)
    emit(
        {
            "phase": "generate",
            "iteration": 0,
            "plan": plan,
            "score": None,
            "approved": None,
            "issues": [],
            "message": "Initial plan generated.",
        }
    )

    if not config.refine:
        emit(
            {
                "phase": "final",
                "iteration": 0,
                "plan": plan,
                "score": None,
                "approved": None,
                "issues": [],
                "message": "Refinement disabled; returning initial plan.",
            }
        )
        return plan

    best_plan = plan
    best_score = -1

    for iteration in range(1, config.maxIterations + 1):
        # A noisy small model can emit a bad critique; don't let that
        # abort the whole run. Keep the best valid plan we have.
        try:
            verdict = critiquePlan(plan, config)
        except ValueError as exc:
            emit(
                {
                    "phase": "critique",
                    "iteration": iteration,
                    "plan": plan,
                    "score": best_score,
                    "approved": None,
                    "issues": [],
                    "message": f"Critique failed: {exc}",
                }
            )
            break

        approved = bool(verdict.get("approved"))
        issues = verdict.get("issues", [])
        issue_count = len(issues)
        try:
            score = int(verdict.get("score", 0))
        except (TypeError, ValueError):
            score = 0

        emit(
            {
                "phase": "critique",
                "iteration": iteration,
                "plan": plan,
                "score": score,
                "approved": approved,
                "issues": issues,
                "message": (
                    f"Critique #{iteration}: score {score}, "
                    f"{issue_count} issue(s), approved={approved}."
                ),
            }
        )

        # Always keep the highest-scored plan seen so far.
        if score > best_score:
            best_score = score
            best_plan = plan

        if approved or issue_count == 0 or score >= config.acceptScore:
            break

        if iteration == config.maxIterations:
            break

        # A failed refine (invalid/empty plan) must not discard the
        # good plan we already have. Keep the best and stop.
        try:
            plan = refinePlan(plan, verdict, config)
            emit(
                {
                    "phase": "refine",
                    "iteration": iteration,
                    "plan": plan,
                    "score": None,
                    "approved": None,
                    "issues": [],
                    "message": f"Refined plan after critique #{iteration}.",
                }
            )
        except ValueError as exc:
            emit(
                {
                    "phase": "refine",
                    "iteration": iteration,
                    "plan": best_plan,
                    "score": best_score,
                    "approved": None,
                    "issues": [],
                    "message": (
                        f"Refine produced an invalid plan ({exc}); "
                        "keeping best plan."
                    ),
                }
            )
            break

    emit(
        {
            "phase": "final",
            "iteration": config.maxIterations,
            "plan": best_plan,
            "score": best_score,
            "approved": None,
            "issues": [],
            "message": f"Final plan selected (best score {best_score}).",
        }
    )
    return best_plan
