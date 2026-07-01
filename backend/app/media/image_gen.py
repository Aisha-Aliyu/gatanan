"""Cinematographer, image stage.
Generates one keyframe per shot with Qwen Cloud's text-to-image model, then
downloads it (generated URLs expire in 24 hours)"""
import re
from pathlib import Path

import dashscope
import requests
from dashscope import ImageSynthesis

from app.config import settings
from app.schemas import Shot, StoryBible

dashscope.api_key = settings.dashscope_api_key
dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

_NEGATIVE = (
    "horror, scary, creepy, frightening, monster, demon, zombie, undead, "
    "skull, human skull, animal skull, bones, skeleton, sharp teeth, fangs, gaunt corpse, "
    "spider legs, insect legs, extra legs, multiple legs, eight legs, extra limbs, extra arms, "
    "web on body, web on skin, "
    "beard, moustache, facial hair, stubble, "
    "creature in bag, animal in sack, face on sack, eyes on sack, lizard, gecko, dragon, "
    "shovel, spade, pitchfork, hay fork, farm fork, trident, modern tools, "
    "metal cauldron, black cooking cauldron, "
    "writing on clothing, text on fabric, letters on cloth, labels on clothes, "
    "on-screen text, caption, subtitle, watermark, logo, signature, "
    "deformed hands, extra fingers, blurry, low quality"
)


_PAREN = re.compile(r"\s*\([^)]*\)")


def _strip_parens(text: str) -> str:
    """Remove parenthetical asides so foreign terms aren't painted on as labels."""
    return _PAREN.sub("", text).strip()


def _name_key(name: str) -> str:
    first = name.split("(")[0].strip()
    words = first.split()
    if len(words) > 1 and words[0].lower() == "the":
        return words[1].lower()
    return words[0].lower() if words else first.lower()


def _characters_in_shot(shot: Shot, bible: StoryBible) -> list:
    desc = shot.description.lower()
    return [c for c in bible.characters if _name_key(c.name) in desc]


def _beat_emotion(shot: Shot, bible: StoryBible) -> str:
    for beat in bible.beats:
        if beat.id == shot.beat_id:
            return beat.emotion
    return ""


def build_image_prompt(shot: Shot, bible: StoryBible) -> str:
    """Assemble the full text-to-image prompt for one shot."""
    present = _characters_in_shot(shot, bible)
    block = " ".join(
        f"{_strip_parens(c.name)}: {_strip_parens(c.visual_notes)}" for c in present
    )
    char_line = f"Characters in frame, render consistently: {block} " if block else ""
    emotion = _beat_emotion(shot, bible)
    emotion_line = (
        f"Emotional tone of this moment: {emotion}. Faces and body language must reflect it. "
        if emotion else ""
    )
    return (
        f"{settings.art_direction} "
        f"Scene: {_strip_parens(shot.description)} "
        f"{emotion_line}"
        f"Visual style for this shot: {shot.visual_style}. "
        f"Authentic {bible.origin} setting; dress, architecture, and objects must match this culture. "
        f"All clothing and fabric is plain, with no writing, letters, or symbols printed on it. "
        f"{char_line}"
        f"Cinematic film still, no on-screen text, no captions, no watermark."
    )


def generate_keyframe(
    prompt: str,
    out_path: Path,
    *,
    model: str | None = None,
    size: str | None = None,
    seed: int | None = None,
) -> Path:
    """Generate one image and save it to out_path. Raises on failure."""
    rsp = ImageSynthesis.call(
        api_key=settings.dashscope_api_key,
        model=model or settings.image_model,
        prompt=prompt,
        negative_prompt=_NEGATIVE,
        n=1,
        size=size or settings.image_size,
        seed=seed if seed is not None else settings.image_seed,
        prompt_extend=False,
        watermark=False,
    )
    if rsp.status_code != 200:
        raise RuntimeError(f"Image API error {rsp.status_code}: {rsp.code} - {rsp.message}")
    results = getattr(rsp.output, "results", None)
    if not results:
        raise RuntimeError(f"No image returned. Full output: {rsp.output}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img = requests.get(results[0].url, timeout=60)
    img.raise_for_status()
    out_path.write_bytes(img.content)
    return out_path
