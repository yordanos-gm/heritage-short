import math
import struct
import time
import wave
from pathlib import Path
from pipeline.utils import (
    OUTPUTS_DIR,
    compute_hash,
    ensure_dirs,
    is_cached,
    load_storyboard,
    log_run,
    write_cache_meta,
)


def synthesize_pentatonic_score(wav_path: Path, duration_sec: float = 95.0, sample_rate: int = 24000):
    """Generates a gentle, warm Ethiopian Tizita-inspired pentatonic ambient underscore."""
    # Tizita major pentatonic frequencies (C4, D4, E4, G4, A4, C5)
    notes = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25]
    melody = [0, 2, 3, 4, 3, 2, 1, 0, 3, 4, 5, 4, 3, 2, 1, 2]
    total_samples = int(duration_sec * sample_rate)
    note_len = int(2.2 * sample_rate)

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(total_samples):
            t = i / sample_rate
            idx = (i // note_len) % len(melody)
            pos = (i % note_len) / note_len
            freq = notes[melody[idx]]

            # Soft plucked krar-like envelope + warm low drone
            env = math.sin(math.pi * min(pos * 4.0, 1.0)) * math.exp(-2.4 * pos)
            pluck = 0.22 * env * (math.sin(2 * math.pi * freq * t) + 0.35 * math.sin(4 * math.pi * freq * t))
            pad = 0.08 * math.sin(2 * math.pi * 130.81 * t) + 0.05 * math.sin(2 * math.pi * 196.00 * t)
            fade = min(t / 2.0, 1.0) * min((duration_sec - t) / 3.0, 1.0)
            val = max(-0.95, min(0.95, (pluck + pad) * fade))
            frames.extend(struct.pack("<h", int(val * 32767)))
        wf.writeframes(bytes(frames))


def main():
    ensure_dirs()
    sb = load_storyboard()
    out_dir = OUTPUTS_DIR / "music"
    custom_score = out_dir / "acestep_score.mp3"
    wav_path = out_dir / "score.wav"
    meta_path = out_dir / "score.json"

    if custom_score.exists():
        print(f"[OK] Using ACE-Step score: {custom_score}")
        log_run("music", "score", "ace-step-1.5", {"file": custom_score.name}, None, 0.0, 0.0, "cached", True)
        return

    cache_key = compute_hash({"music_prompt": sb["music_prompt"], "engine": "tizita-synth-v1"})
    if is_cached(wav_path, meta_path, cache_key):
        print("[CACHE] Background score unchanged.")
        log_run("music", "score", "tizita-synth-v1", {}, None, 0.0, 0.0, "cached", True)
        return

    print("[GEN] Generating warm Ethiopian pentatonic background score...")
    t0 = time.perf_counter()
    synthesize_pentatonic_score(wav_path, duration_sec=95.0)
    latency = time.perf_counter() - t0
    write_cache_meta(meta_path, cache_key, {"music_prompt": sb["music_prompt"], "engine": "tizita-synth-v1"})
    log_run("music", "score", "tizita-synth-v1", {"duration_sec": 95.0}, 1975, latency, 0.0, "ok", False)
    print(f"[OK] Score saved at {wav_path} ({latency:.2f}s).")


if __name__ == "__main__":
    main()