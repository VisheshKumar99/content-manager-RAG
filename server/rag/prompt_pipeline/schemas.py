from typing import Literal
from pydantic import BaseModel, Field, model_validator


class VideoConfig(BaseModel):
    contentType: str = "cinematic"
    contentFormat: Literal["reel", "short", "long_video"] = "reel"
    viewType: Literal["portrait", "landscape", "square"] = "portrait"
    contentPlatform: list[str] = ["youtube", "instagram"]
    videoLength: int = Field(default=30, gt=0)
    onePromptLength: int = Field(default=6, gt=0)
    detailLevel: Literal["medium", "high", "very_high"] = "very_high"
    language: str = "English"

    @model_validator(mode="after")
    def validate_lengths(self):
        if self.onePromptLength > self.videoLength:
            raise ValueError(
                "Clip length cannot exceed total video length"
            )
        return self