import shutil
import subprocess
import time
from pathlib import Path
import imageio_ffmpeg
from pipeline.utils import (
    OUTPUTS_DIR,
    compute_hash,
    ensure_dirs,
    is_cached,
    load_storyboard,
    log_run,
    write_cache_meta,
)

FFMPEG = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()


def get_audio_duration(audio_path: Path) -> float:
    # Probe duration via ffmpeg stderr
    proc = subprocess.run([FFMPEG, "-i", str(audio_path)], capture_output=True, text=True)
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            t_str = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t_str.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 8.0


def build_shot_clip(shot: dict) -> Path:
    shot_id = shot["shot_id"]
    img_path = OUTPUTS_DIR / "keyframes" / f"shot_{shot_id:02d}.png"
    audio_mp3 = OUTPUTS_DIR / "narration" / f"shot_{shot_id:02d}.mp3"
    audio_wav = OUTPUTS_DIR / "narration" / f"shot_{shot_id:02d}.wav"
    audio_path = audio_wav if audio_wav.exists() else audio_mp3

    # Match shot length to narration + 0.6s breathing room
    dur = max(float(shot["duration_sec"]), get_audio_duration(audio_path) + 0.6)
    fps = 24
    frames = int(dur * fps)

    # Alternate gentle zoom-in and zoom-out so consecutive shots feel cinematic
    if shot_id % 2 == 1:
        zp = f"zoompan=z='min(zoom+0.0008,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps={fps}"
    else:
        zp = f"zoompan=z='if(lte(zoom,1.0),1.15,max(1.0,zoom-0.0008))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps={fps}"

    out_dir = OUTPUTS_DIR / "shots"
    clip_path = out_dir / f"shot_{shot_id:02d}.mp4"
    meta_path = out_dir / f"shot_{shot_id:02d}.json"

    cache_key = compute_hash({
        "img_mtime": img_path.stat().st_mtime_ns,
        "dur": round(dur, 2),
        "motion": shot["motion_prompt"],
        "zp": zp,
    })

    if is_cached(clip_path, meta_path, cache_key):
        print(f"[CACHE] Shot {shot_id:02d} video clip unchanged.")
        log_run("shots", shot_id, "ffmpeg-ken-burns", {"dur": round(dur, 2)}, shot["seed"], 0.0, 0.0, "cached", True)
        return clip_path

    print(f"[GEN] Rendering moving shot {shot_id:02d} ({dur:.1f}s)...")
    t0 = time.perf_counter()
    subprocess.run(
        [
            FFMPEG, "-y",
            "-loop", "1", "-i", str(img_path),
            "-vf", f"scale=1920:-2,{zp},format=yuv420p",
            "-t", f"{dur:.2f}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            str(clip_path),
        ],
        check=True,
        capture_output=True,
    )
    latency = time.perf_counter() - t0
    write_cache_meta(meta_path, cache_key, {"dur": round(dur, 2), "engine": "ffmpeg-ken-burns"})
    log_run("shots", shot_id, "ffmpeg-ken-burns", {"dur": round(dur, 2)}, shot["seed"], latency, 0.0, "ok", False)
    print(f"[OK] Shot {shot_id:02d} clip saved ({latency:.2f}s).")
    return clip_path


def main():
    ensure_dirs()
    sb = load_storyboard()
    for shot in sb["shots"]:
        build_shot_clip(shot)


if __name__ == "__main__":
    main()