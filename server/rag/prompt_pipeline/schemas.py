from typing import Literal
from pydantic import BaseModel, Field, model_validator


class VideoConfig(BaseModel):
    contentType: Literal[
        "cinematic",
        "anime",
        "cartoon",
        "3d_animation",
        "realistic",
        "documentary",
    ] = "cinematic"
    contentFormat: Literal["reel", "short", "long_video"] = "reel"
    viewType: Literal["portrait", "landscape", "square"] = "portrait"
    contentPlatform: list[str] = ["youtube", "instagram"]
    videoLength: int = Field(default=30, gt=0)
    onePromptLength: int = Field(default=6, gt=0)
    detailLevel: Literal["medium", "high", "very_high"] = "very_high"
    language: str = "English"

    # Self-refinement loop controls
    refine: bool = True
    maxIterations: int = Field(default=3, ge=1, le=10)
    acceptScore: int = Field(default=85, ge=0, le=100)

    @model_validator(mode="after")
    def validate_lengths(self):
        if self.onePromptLength > self.videoLength:
            raise ValueError(
                "Clip length cannot exceed total video length"
            )
        return self