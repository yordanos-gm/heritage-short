import json
import shutil
import subprocess
import textwrap
import time
from pathlib import Path
import imageio_ffmpeg
from pipeline.utils import (
    OUTPUTS_DIR,
    ROOT_DIR,
    ensure_dirs,
    load_storyboard,
    log_run,
)

FFMPEG = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()


def fmt_srt_time(seconds: float) -> str:
    ms = int(round((seconds - int(seconds)) * 1000))
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def get_shot_duration(shot_id: int, fallback: float) -> float:
    meta_path = OUTPUTS_DIR / "shots" / f"shot_{shot_id:02d}.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if "dur" in meta:
            return float(meta["dur"])
    return float(fallback)


def build_subtitles(sb: dict, durations: list[float], srt_path: Path):
    lines = []
    t = 0.0
    for idx, (shot, dur) in enumerate(zip(sb["shots"], durations), start=1):
        start = fmt_srt_time(t + 0.2)
        end = fmt_srt_time(t + dur - 0.2)
        wrapped = "\n".join(textwrap.wrap(shot["subtitles_en"], width=38)[:2])
        lines.append(f"{idx}\n{start} --> {end}\n{wrapped}\n")
        t += dur
    srt_path.write_text("\n".join(lines), encoding="utf-8")


def build_synced_narration(sb: dict, durations: list[float], out_wav: Path):
    padded_files = []
    nar_dir = OUTPUTS_DIR / "narration"
    tmp_dir = OUTPUTS_DIR / "final" / "tmp_audio"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for shot, dur in zip(sb["shots"], durations):
        sid = shot["shot_id"]
        src = nar_dir / f"shot_{sid:02d}.wav"
        if not src.exists():
            src = nar_dir / f"shot_{sid:02d}.mp3"
        padded = tmp_dir / f"padded_{sid:02d}.wav"
        subprocess.run(
            [
                FFMPEG, "-y", "-i", str(src),
                "-af", f"apad=whole_dur={dur:.2f}",
                "-ar", "44100", "-ac", "2",
                str(padded),
            ],
            check=True,
            capture_output=True,
        )
        padded_files.append(padded)

    concat_txt = tmp_dir / "audio_concat.txt"
    concat_txt.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in padded_files),
        encoding="utf-8",
    )
    subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c:a", "pcm_s16le", str(out_wav)],
        check=True,
        capture_output=True,
    )


def mix_audio_with_ducking(voice_wav: Path, score_path: Path, total_dur: float, mixed_wav: Path):
    # Sidechain compression ducks the music whenever the narrator speaks, then normalizes to -14 LUFS
    filter_complex = (
        "[0:a]aformat=sample_rates=44100:channel_layouts=stereo,apad=pad_dur=3,asplit=2[voice_sc][voice_mix];"
        "[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.35[music_low];"
        "[music_low][voice_sc]sidechaincompress=threshold=0.02:ratio=6:attack=300:release=1500[music_ducked];"
        "[voice_mix][music_ducked]amix=inputs=2:duration=longest:normalize=0,"
        "loudnorm=I=-14:TP=-1:LRA=11[aout]"
    )
    subprocess.run(
        [
            FFMPEG, "-y",
            "-i", str(voice_wav),
            "-stream_loop", "-1", "-i", str(score_path),
            "-t", f"{total_dur + 3.0:.2f}",
            "-filter_complex", filter_complex,
            "-map", "[aout]",
            "-ar", "44100", "-ac", "2",
            str(mixed_wav),
        ],
        check=True,
        capture_output=True,
    )


def make_end_card(out_mp4: Path, width: int, height: int):
    font = "C\\:/Windows/Fonts/arial.ttf"
    title_size = 36 if width > height else 28
    sub_size = 24 if width > height else 20
    vf = (
        f"drawtext=fontfile='{font}':text='Made with AI':"
        f"fontcolor=white:fontsize={title_size}:x=(w-text_w)/2:y=(h-text_h)/2-25,"
        f"drawtext=fontfile='{font}':text='Visuals - FLUX.1 Schnell | Voice - Edge-TTS | Assembly - FFmpeg':"
        f"fontcolor=0xCCCCCC:fontsize={sub_size}:x=(w-text_w)/2:y=(h-text_h)/2+25"
    )
    subprocess.run(
        [
            FFMPEG, "-y",
            "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:r=24:d=3",
            "-vf", f"{vf},format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            str(out_mp4),
        ],
        check=True,
        capture_output=True,
    )


def main():
    ensure_dirs()
    t0 = time.perf_counter()
    sb = load_storyboard()
    final_dir = OUTPUTS_DIR / "final"

    durations = [get_shot_duration(s["shot_id"], s["duration_sec"]) for s in sb["shots"]]
    total_dur = sum(durations)
    print(f"[ASM] Assembling {len(sb['shots'])} shots ({total_dur:.1f}s + 3.0s AI end card)...")

    # 1. Subtitles
    srt_path = final_dir / "subtitles.srt"
    build_subtitles(sb, durations, srt_path)

    # 2. Synced narration + ducked/normalized mix
    voice_wav = final_dir / "voice_synced.wav"
    build_synced_narration(sb, durations, voice_wav)

    score_path = OUTPUTS_DIR / "music" / "acestep_score.mp3"
    if not score_path.exists():
        score_path = OUTPUTS_DIR / "music" / "score.wav"
    mixed_wav = final_dir / "mixed_audio.wav"
    mix_audio_with_ducking(voice_wav, score_path, total_dur, mixed_wav)

    # 3. Concatenate video clips
    clips_txt = final_dir / "clips_concat.txt"
    clips_txt.write_text(
        "\n".join(f"file '{(OUTPUTS_DIR / 'shots' / f'shot_{s['shot_id']:02d}.mp4').as_posix()}'" for s in sb["shots"]),
        encoding="utf-8",
    )
    raw_16x9 = final_dir / "raw_16x9.mp4"
    subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(clips_txt), "-c", "copy", str(raw_16x9)],
        check=True,
        capture_output=True,
    )

    # 4. Export 16:9 with burned-in subtitles + 3s AI end card
    end_16x9 = final_dir / "end_16x9.mp4"
    make_end_card(end_16x9, 1280, 720)
    sub_16x9 = final_dir / "sub_16x9.mp4"
    srt_rel = srt_path.relative_to(ROOT_DIR).as_posix()

    subprocess.run(
        [
            FFMPEG, "-y", "-i", str(raw_16x9),
            "-vf", f"subtitles='{srt_rel}':force_style='FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,MarginV=35'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            str(sub_16x9),
        ],
        check=True,
        capture_output=True,
        cwd=str(ROOT_DIR),
    )

    film_16x9 = final_dir / "film_16x9.mp4"
    subprocess.run(
        [
            FFMPEG, "-y",
            "-i", str(sub_16x9),
            "-i", str(end_16x9),
            "-i", str(mixed_wav),
            "-filter_complex", "[0:v]setsar=1[v0];[1:v]setsar=1[v1];[v0][v1]concat=n=2:v=1:a=0[vout]",
            "-map", "[vout]", "-map", "2:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", 
            str(film_16x9),
        ],
        check=True,
        capture_output=True,
    )
    print(f"[OK] Exported horizontal 16:9 film: {film_16x9}")

    # 5. Export 9:16 vertical (center crop + safe-area subtitles + 3s AI end card)
    end_9x16 = final_dir / "end_9x16.mp4"
    make_end_card(end_9x16, 720, 1280)
    sub_9x16 = final_dir / "sub_9x16.mp4"

    subprocess.run(
        [
            FFMPEG, "-y", "-i", str(raw_16x9),
            "-vf", f"crop=ih*9/16:ih,scale=720:1280,subtitles='{srt_rel}':force_style='FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,MarginV=120'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            str(sub_9x16),
        ],
        check=True,
        capture_output=True,
        cwd=str(ROOT_DIR),
    )

    film_9x16 = final_dir / "film_9x16.mp4"
    subprocess.run(
        [
            FFMPEG, "-y",
            "-i", str(sub_9x16),
            "-i", str(end_9x16),
            "-i", str(mixed_wav),
            "-filter_complex", "[0:v]setsar=1[v0];[1:v]setsar=1[v1];[v0][v1]concat=n=2:v=1:a=0[vout]",
            "-map", "[vout]", "-map", "2:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", 
            str(film_9x16),
        ],
        check=True,
        capture_output=True,
    )
    latency = time.perf_counter() - t0
    log_run("assemble", "final", "ffmpeg-assemble", {"exports": ["16x9", "9x16"], "total_sec": round(total_dur + 3.0, 1)}, None, latency, 0.0, "ok", False)
    print(f"[OK] Exported vertical 9:16 film: {film_9x16} ({latency:.2f}s total).")


if __name__ == "__main__":
    main()