"""FastAPI service exposing the Gatanan showrunner pipeline.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agents.director import plan_shots
from app.agents.griot import extract_story_bible
from app.config import settings
from app.schemas import ShotList, StoryBible

app = FastAPI(
    title="Gatanan Showrunner API",
    description=(
        "A multi-agent pipeline that turns an African oral folktale into a film "
        "plan (Story Bible + Shot List), powered by Qwen Cloud."
    ),
    version="1.0.0",
)

# Allow a browser frontend (for example, hosted on Netlify) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaleRequest(BaseModel):
    tale_text: str = Field(min_length=20, description="The folktale text to adapt.")
    target_seconds: int = Field(default=75, ge=20, le=180)
    max_video_shots: int = Field(default=3, ge=0, le=8)


class PlanResponse(BaseModel):
    bible: StoryBible
    shot_list: ShotList
    total_seconds: float
    video_count: int


@app.get("/")
def root() -> dict:
    """Health check. Confirms the service is live and which Qwen Cloud endpoint it calls."""
    return {
        "service": "Gatanan Showrunner API",
        "status": "running",
        "powered_by": "Qwen Cloud (Alibaba Model Studio)",
        "qwen_cloud_endpoint": settings.dashscope_base_url,
        "text_model": settings.text_model,
        "image_model": settings.image_model,
    }


@app.post("/story-bible", response_model=StoryBible)
def story_bible(req: TaleRequest) -> StoryBible:
    """Griot agent: distil a folktale into a structured Story Bible (one Qwen Cloud call)."""
    try:
        return extract_story_bible(req.tale_text)
    except Exception as exc:  # surface upstream errors as a clean 502
        raise HTTPException(status_code=502, detail=f"Griot failed: {exc}") from exc


@app.post("/plan", response_model=PlanResponse)
def plan(req: TaleRequest) -> PlanResponse:
    """Full planning pipeline: the Griot builds the Bible, the Director plans the Shot List."""
    try:
        bible = extract_story_bible(req.tale_text)
        shots = plan_shots(
            bible,
            target_seconds=req.target_seconds,
            max_video_shots=req.max_video_shots,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Pipeline failed: {exc}") from exc
    return PlanResponse(
        bible=bible,
        shot_list=shots,
        total_seconds=shots.total_seconds,
        video_count=shots.video_count,
    )
