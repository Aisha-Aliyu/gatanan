import sys
from pathlib import Path

from app.media.image_gen import build_image_prompt, generate_keyframe
from app.schemas import ShotList, StoryBible

OUTPUT = Path("output")
IMAGES = OUTPUT / "images"


def main() -> None:
    bible = StoryBible.model_validate_json(
        (OUTPUT / "story_bible.json").read_text(encoding="utf-8")
    )
    shots = ShotList.model_validate_json(
        (OUTPUT / "shot_list.json").read_text(encoding="utf-8")
    )

    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else None  # set to re-roll one shot

    if arg == "all":
        targets = shots.shots
    else:
        targets = [s for s in shots.shots if s.id == int(arg)]
        if not targets:
            print(f"No shot with id {arg}")
            sys.exit(1)

    failures = []
    for shot in targets:
        prompt = build_image_prompt(shot, bible)
        out = IMAGES / f"shot_{shot.id:02d}.png"
        tag = f" (seed {seed})" if seed is not None else ""
        print(f"Shot {shot.id} ({shot.render_mode}){tag}: generating...")
        try:
            generate_keyframe(prompt, out, seed=seed)
            print(f"  saved {out}")
        except Exception as exc:
            print(f"  FAILED: {exc}")
            failures.append((shot.id, str(exc)))

    print()
    if failures:
        print(f"{len(failures)} shot(s) failed:")
        for sid, err in failures:
            print(f"  shot {sid}: {err}")
    else:
        print(f"Done. {len(targets)} image(s) saved in {IMAGES}/")


if __name__ == "__main__":
    main()
