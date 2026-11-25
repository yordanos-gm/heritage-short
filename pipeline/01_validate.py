import json
from jsonschema import validate
from pipeline.utils import ROOT_DIR, ensure_dirs, load_storyboard


def main():
    ensure_dirs()
    storyboard = load_storyboard()
    with open(ROOT_DIR / "schema" / "storyboard.schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)

    validate(instance=storyboard, schema=schema)
    total_sec = sum(s["duration_sec"] for s in storyboard["shots"])
    print(f"[OK] Validated '{storyboard['title']}' ({len(storyboard['shots'])} shots, {total_sec}s total).")


if __name__ == "__main__":
    main()