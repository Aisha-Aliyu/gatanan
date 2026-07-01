import sys
from pathlib import Path

from app.agents.director import plan_shots
from app.agents.griot import extract_story_bible

OUTPUT_DIR = Path("output")


def main() -> None:
    tale_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tales/fisherman.txt")
    if not tale_path.exists():
        print(f"Tale not found: {tale_path}")
        sys.exit(1)

    tale = tale_path.read_text(encoding="utf-8")
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Griot is reading: {tale_path.name}\n")
    bible = extract_story_bible(tale)
    (OUTPUT_DIR / "story_bible.json").write_text(
        bible.model_dump_json(indent=2), encoding="utf-8"
    )
    print(f"Title:      {bible.title}")
    print(f"Origin:     {bible.origin}")
    print(f"Moral:      {bible.moral}")
    print(f"Characters: {', '.join(c.name for c in bible.characters)}")
    print(f"Beats:      {len(bible.beats)}")
    print("Saved output/story_bible.json\n")

    print("Director is planning shots...\n")
    shots = plan_shots(bible, target_seconds=75, max_video_shots=3)
    (OUTPUT_DIR / "shot_list.json").write_text(
        shots.model_dump_json(indent=2), encoding="utf-8"
    )
    for shot in shots.shots:
        tag = "VIDEO" if shot.render_mode == "video" else "still"
        print(f"  [{shot.id:>2}] {tag:5} {shot.duration_seconds:>4.1f}s  beat {shot.beat_id}  {shot.description[:55]}")

    still_count = len(shots.shots) - shots.video_count
    print(
        f"\nTotal: {shots.total_seconds:.0f}s across {len(shots.shots)} shots "
        f"({shots.video_count} video, {still_count} still)"
    )
    print("Saved output/shot_list.json\n")
    print("Day 2 done.")


if __name__ == "__main__":
    main()
