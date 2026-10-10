import json

from rag.llm.factory import get_llm
from rag.prompt_pipeline.schemas import VideoConfig

llm = get_llm()

SYSTEM_PROMPT = """
You are an expert film director, screenwriter, cinematographer,
character designer, and AI video prompt engineer.

Your task is to transform a raw user idea into a production-ready
AI video generation plan.

RULES:

1. STORY
- Turn the raw idea into a coherent, emotionally engaging story.
- Include a hook, progression, conflict or curiosity, and a payoff.
- Every clip must advance the story.
- Avoid disconnected scenes and unnecessary filler.

2. CHARACTERS
- Create one reference prompt per unique character.
- Specify age, proportions, face, eyes, hair, clothing, colors,
  accessories, personality, and distinguishing features.
- Include a full-body design, facial details, and reference views
  in the design prompt when appropriate.
- Assign a stable characterId to each character.
- Keep appearance consistent across every clip.

3. ENVIRONMENTS
- Create reusable environment reference prompts.
- Specify layout, objects, materials, colors, atmosphere,
  lighting, weather, and time of day.
- Assign a stable environmentId.

4. VIDEO CLIPS
- Generate the exact number of clips required by the duration.
- Each clip represents one continuous shot.
- Each video prompt must be independently usable by a video model.
- Describe subject, action, setting, camera movement, shot size,
  composition, lighting, motion, mood, and visual details.
- Describe what happens during the clip, not just a static image.
- Connect every clip to the previous and next clip.
- Preserve character appearance, clothing, props, geography,
  lighting continuity, and story state.
- Avoid excessive actions that cannot fit within the clip duration.

5. PLATFORM AND FORMAT
- Follow the requested visual aspect ratio and content style.
- For portrait content, prioritize vertical composition.
- For landscape content, prioritize cinematic wide composition.
- Make the opening engaging and the ending satisfying.
- Avoid logos, watermarks, and unintended text.

6. OUTPUT
- Return valid JSON only.
- Follow the requested output schema.
- Do not include Markdown fences or commentary.
- Return one character reference prompt per unique character.
- Return one environment reference prompt per unique environment.
- Return one video prompt per clip.
- Do not omit required fields.
"""


def promptRectifyPipeline(prompt: str, config: VideoConfig) -> dict:

    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    clip_count = (
        config.videoLength + config.onePromptLength - 1
    ) // config.onePromptLength

    durations = [
        min(config.onePromptLength, config.videoLength - i * config.onePromptLength)
        for i in range(clip_count)
    ]

    user_request = {
        "rawIdea": prompt,
        "configuration": config.model_dump(),
        "clipPlan": {
            "numberOfClips": clip_count,
            "clipDurationsSeconds": durations,
            "totalDurationSeconds": config.videoLength,
        },
        "outputRequirements": {
            "storyline": True,
            "characterReferencePrompts": True,
            "environmentReferencePrompts": True,
            "videoPrompts": True,
            "continuityRules": True,
            "cameraAndMotionDetails": True,
            "audioPrompts": True,
            "returnFormat": "JSON",
        },
    }

    full_prompt = f"""
{SYSTEM_PROMPT}

Create the video plan for this request:

{json.dumps(user_request, ensure_ascii=False, indent=2)}

Return the complete JSON object.
"""

    response = llm.generate(full_prompt)

    try:
        result = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "LLM returned invalid JSON. Retry or repair the response."
        ) from exc

    clips = result.get("clips", [])

    if len(clips) != clip_count:
        raise ValueError(f"Expected {clip_count} clips, received {len(clips)}")

    actual_duration = sum(clip.get("durationSeconds", 0) for clip in clips)

    if actual_duration != config.videoLength:
        raise ValueError(
            f"Expected {config.videoLength}s, " f"received {actual_duration}s"
        )

    return result
