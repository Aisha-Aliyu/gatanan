"""Data contracts"""

from typing import Literal

from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str = Field(description="The character's name, in the tale's own tradition.")
    role: str = Field(description="protagonist, antagonist, helper, narrator, etc.")
    description: str = Field(description="Personality and part in the story.")
    visual_notes: str = Field(
        description="Appearance grounded in the culture of origin: attire, features, bearing."
    )


class Beat(BaseModel):
    id: int = Field(description="Order of this beat in the story, starting at 1.")
    summary: str = Field(description="What happens, in one or two sentences.")
    emotion: str = Field(description="The dominant emotion of this beat.")
    setting: str = Field(description="Where this beat takes place.")


class StoryBible(BaseModel):
    title: str
    logline: str = Field(description="The whole tale distilled into one sentence.")
    origin: str = Field(description="Cultural origin, e.g. 'Hausa (Kano, Nigeria)'.")
    moral: str = Field(description="The lesson the tale teaches.")
    cultural_motifs: list[str] = Field(
        description="Specific elements to preserve: objects, customs, naming, setting."
    )
    characters: list[Character]
    beats: list[Beat]


RenderMode = Literal["video", "still"]


class Shot(BaseModel):
    id: int = Field(description="Order of this shot, starting at 1.")
    beat_id: int = Field(description="The id of the story beat this shot illustrates.")
    description: str = Field(description="The visual content of the shot.")
    render_mode: RenderMode = Field(
        description="'video' for motion-critical beats, 'still' for a held image with subtle motion."
    )
    duration_seconds: float = Field(gt=0, le=15, description="How long this shot runs.")
    visual_style: str = Field(description="Palette, mood, framing, lighting.")
    motion: str = Field(description="Camera or subject motion, e.g. 'slow push in'.")
    narration: str = Field(description="The narrator's line spoken over this shot.")


class ShotList(BaseModel):
    shots: list[Shot]

    @property
    def total_seconds(self) -> float:
        return sum(shot.duration_seconds for shot in self.shots)

    @property
    def video_count(self) -> int:
        return sum(1 for shot in self.shots if shot.render_mode == "video")
