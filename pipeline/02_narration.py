import asyncio
import os
import shutil
import subprocess
import time
import wave
from pathlib import Path
import edge_tts
from google import genai
from google.genai import types
from pipeline.utils import (
    OUTPUTS_DIR,
    compute_hash,
    ensure_dirs,
    is_cached,
    load_storyboard,
    log_run,
    write_cache_meta,
)

GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_VOICE = "Enceladus"
FALLBACK_MODEL = "edge-tts/am-ET-AmehaNeural"
FALLBACK_VOICE = "am-ET-AmehaNeural"


def save_audio_bytes(audio_bytes: bytes, mime_type: str, out_path: Path, sample_rate: int = 24000):
    if "wav" in (mime_type or "").lower():
        out_path.write_bytes(audio_bytes)
    else:
        with wave.open(str(out_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_bytes)


async def _run_edge_tts(text: str, mp3_path: Path):
    communicate = edge_tts.Communicate(text, voice=FALLBACK_VOICE, rate="-5%")
    await communicate.save(str(mp3_path))


def generate_shot_audio(client: genai.Client, shot: dict, language: str) -> Path:
    shot_id = shot["shot_id"]
    text = shot["narration_local"]
    cache_key = compute_hash({
        "language": language,
        "text": text,
        "primary": GEMINI_MODEL,
        "fallback": FALLBACK_VOICE,
    })

    out_dir = OUTPUTS_DIR / "narration"
    wav_path = out_dir / f"shot_{shot_id:02d}.wav"
    mp3_path = out_dir / f"shot_{shot_id:02d}.mp3"
    meta_path = out_dir / f"shot_{shot_id:02d}.json"

    for candidate in (wav_path, mp3_path):
        if is_cached(candidate, meta_path, cache_key):
            print(f"[CACHE] Shot {shot_id:02d} narration unchanged ({candidate.name}).")
            log_run("narration", shot_id, "cache", {"file": candidate.name}, None, 0.0, 0.0, "cached", True)
            return candidate

    # 1. Try Gemini 3.8 Flash TTS once first
    print(f"[GEN] Generating Amharic narration for Shot {shot_id:02d}...")
    t0 = time.perf_counter()
    try:
        prompt = f"Read this Amharic narration aloud in a warm, nostalgic storytelling voice. Do not add extra words: {text}"
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=GEMINI_VOICE)
                    )
                ),
            ),
        )
        parts = response.candidates[0].content.parts
        audio_part = next((p for p in parts if getattr(p, "inline_data", None) and p.inline_data.data), None)
        if not audio_part:
            raise RuntimeError("Model returned no inline audio data.")
        save_audio_bytes(audio_part.inline_data.data, audio_part.inline_data.mime_type, wav_path)
        latency = time.perf_counter() - t0
        write_cache_meta(meta_path, cache_key, {"model": GEMINI_MODEL, "file": wav_path.name, "text": text})
        log_run("narration", shot_id, GEMINI_MODEL, {"voice": GEMINI_VOICE}, None, latency, 0.0, "ok", False)
        print(f"[OK] Shot {shot_id:02d} saved via Gemini ({latency:.2f}s).")
        return wav_path
    except Exception as e:
        latency = time.perf_counter() - t0
        log_run("narration", shot_id, GEMINI_MODEL, {"error": str(e)[:180]}, None, latency, 0.0, "fallback", False)
        print(f"[FALLBACK] Gemini unavailable for Shot {shot_id:02d} ({str(e)[:80]}). Using native Amharic edge-tts...")

    # 2. Automatic zero-cost fallback: native Amharic neural voice
    t1 = time.perf_counter()
    asyncio.run(_run_edge_tts(text, mp3_path))
    latency = time.perf_counter() - t1
    write_cache_meta(meta_path, cache_key, {"model": FALLBACK_MODEL, "file": mp3_path.name, "text": text})
    log_run("narration", shot_id, FALLBACK_MODEL, {"voice": FALLBACK_VOICE, "rate": "-5%"}, None, latency, 0.0, "ok", False)
    print(f"[OK] Shot {shot_id:02d} saved via {FALLBACK_VOICE} ({latency:.2f}s).")
    return mp3_path


def build_radio_cut(audio_files: list[Path]):
    if not shutil.which("ffmpeg"):
        print("[INFO] FFmpeg not installed yet. All 10 Amharic audio files are ready in outputs\\narration\\!")
        return

    radio_dir = OUTPUTS_DIR / "radio_cut"
    list_file = radio_dir / "concat.txt"
    full_voice = radio_dir / "voice_full.mp3"
    radio_mp4 = radio_dir / "radio_cut.mp4"

    with open(list_file, "w", encoding="utf-8") as f:
        for a in audio_files:
            f.write(f"file '{a.as_posix()}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c:a", "libmp3lame", "-q:a", "2", str(full_voice)],
        check=True,
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=24",
            "-i", str(full_voice),
            "-f", "lavfi", "-i", "anoisesrc=color=pink:amplitude=0.004",
            "-filter_complex", "[1:a]volume=1.0[v];[2:a]lowpass=f=400[bg];[v][bg]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
            str(radio_mp4),
        ],
        check=True,
    )
    print(f"[DONE] Radio cut ready at: {radio_mp4}")


def main():
    ensure_dirs()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or "PASTE_" in api_key:
        raise ValueError("Set your real GEMINI_API_KEY in .env first!")

    sb = load_storyboard()
    client = genai.Client(api_key=api_key)
    audio_files = [generate_shot_audio(client, shot, sb["language"]) for shot in sb["shots"]]
    build_radio_cut(audio_files)


if __name__ == "__main__":
    main()