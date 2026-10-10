
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

print(result["storyline"])

for character in result["characters"]:
    print("\nCHARACTER:", character["name"])
    print(character["designPrompt"])

for environment in result["environments"]:
    print("\nENVIRONMENT:", environment["name"])
    print(environment["designPrompt"])

for clip in result["clips"]:
    print(f"\nCLIP {clip['clipNumber']}")
    print(f"Duration: {clip['durationSeconds']}s")
    print(clip["videoPrompt"])