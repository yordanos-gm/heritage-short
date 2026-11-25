import subprocess
import sys

STAGES = [
    "pipeline.01_validate",
    "pipeline.02_narration",
    "pipeline.03_keyframes",
    "pipeline.04_shots",
    "pipeline.05_music",
    "pipeline.06_assemble",
]


def main():
    for stage in STAGES:
        print(f"\n=== Running {stage} ===")
        subprocess.run([sys.executable, "-m", stage], check=True)
    print("\n[DONE] Pipeline complete! Check outputs/final/film_16x9.mp4 and film_9x16.mp4")


if __name__ == "__main__":
    main()