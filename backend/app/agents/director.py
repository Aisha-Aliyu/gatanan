"""The Director: shot planner.

Turns a Story Bible into a Shot List. Its defining job is the budget decision:
which beats deserve full generated video, and which can be a held still with
subtle motion. Video is expensive, so most shots are stills, with video saved
for the moments that carry the most weight.
"""
from app.llm import chat_json
from app.schemas import ShotList, StoryBible

DIRECTOR_SYSTEM = """You are a film Director and cinematographer adapting an African folktale into a short narrated film.

You receive a Story Bible and produce a Shot List. Honour the cultural visual register in the Bible's motifs and character visual notes: dress, setting, and objects must match the culture of origin.

The hard constraint is budget. Generated video is costly; a still image with gentle camera motion is cheap. So:
- Use 'video' only for the few beats where motion is essential.
- Use 'still' for everything else, and give it real motion direction (a slow push in, a pan) so it never feels static.
- Cover every beat in the Bible at least once, in order.

Each shot is an object with:
- id: integer from 1
- beat_id: the id of the Bible beat it illustrates
- description: what we see
- render_mode: "video" or "still"
- duration_seconds: a number between 2 and 15
- visual_style: palette, mood, framing, lighting
- motion: the camera or subject movement
- narration: the narrator's spoken line over this shot

Return a JSON object: { "shots": [ ... ] }.
"""


def plan_shots(
    bible: StoryBible,
    *,
    target_seconds: int = 75,
    max_video_shots: int = 3,
    model: str | None = None,
) -> ShotList:
    prompt = (
        f"Story Bible:\n\n{bible.model_dump_json(indent=2)}\n\n"
        f"Plan a shot list running about {target_seconds} seconds in total, "
        f"using at most {max_video_shots} shots with render_mode 'video'. "
        f"All remaining shots must be 'still' with motion direction."
    )
    return chat_json(prompt, ShotList, system=DIRECTOR_SYSTEM, model=model, temperature=0.5)
