
from dotenv import load_dotenv
from rag.prompt_pipeline.schemas import VideoConfig
from rag.prompt_pipeline.prompt_builder import promptRectifyPipeline

load_dotenv()

config = VideoConfig(
    contentType="cinematic",
    contentFormat="reel",
    viewType="portrait",
    contentPlatform=["youtube", "instagram"],
    videoLength=30,
    onePromptLength=6,
    detailLevel="very_high"
)

result = promptRectifyPipeline(
    prompt=(
        "A little robot finds a dying flower in a deserted city "
        "and tries to bring it back to life."
    ),
    config=config
)

print(result)

for character in result["characters"]:
    print("\nCHARACTER:", character["name"])
    print(character["designPrompt"])

for environment in result["environments"]:
    print("\nENVIRONMENT:", environment["name"])
    print(environment["designPrompt"])

for clip in result["clips"]:
    print(f"\nCLIP {clip['clipNumber']}  ({clip['durationSeconds']}s)")
    print(f"  Shot:      {clip.get('shotType')}")
    print(f"  Angle:     {clip.get('cameraAngle')}")
    print(f"  Movement:  {clip.get('cameraMovement')}")
    print(f"  Lighting:  {clip.get('lighting')}")
    print(f"  Emotion:   {clip.get('facialEmotion')}")
    print(f"  Framing:   {clip.get('composition')}")
    print(f"  Mood:      {clip.get('mood')}")
    print(f"  Prompt:    {clip.get('videoPrompt')}")
    print(f"  Audio:     {clip.get('audioPrompt')}")