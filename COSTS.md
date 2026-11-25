# Cost Breakdown, Latency & Efficiency Report

## Summary
- **Actual Production Spend:** **$0.00** (100% free tiers + local execution)
- **List-Price Equivalent (Paid APIs):** **~$0.036** for a full 10-shot run
- **Cloud GPU Minutes Used:** **0.0 min** (replaced Kaggle GPU queue with deterministic local FFmpeg Ken Burns motion + serverless Cloudflare Workers AI)
- **End-to-End Cold Run Latency:** **~70–80s** (vs. **< 5s** on cached reruns)

## Per-Stage Cost, Latency & List-Price Equivalent

| Stage | Provider / Engine | Usage (10 Shots) | Measured Latency | GPU Minutes | List-Price Equivalent | Actual Spend |
|---|---|---|---|---|---|---|
| `01_validate` | Local Python | 1 run | < 0.1s | 0.0 | $0.00 | $0.00 |
| `02_narration` | Gemini 3.8 Flash (primary) → `edge-tts` (`am-ET-AmehaNeural` fallback) | 10 clips (~84.6s, ~1,000 chars) | ~25.5s (~2.55s/shot) | 0.0 | ~$0.015 *(Azure Neural TTS list rate: $15 / 1M chars)* | $0.00 |
| `03_keyframes` | Cloudflare Workers AI (`@cf/black-forest-labs/flux-1-schnell`) | 11 images (ref + 10 shots, 4 steps) | ~27.0s (~2.45s/img) | Serverless (~1,900 / 10,000 free daily neurons) | ~$0.021 *(Cloudflare list rate: $0.011 / 1,000 neurons; ~$0.0019/img)* | $0.00 |
| `04_shots` | Local FFmpeg (`imageio-ffmpeg` `zoompan`) | 10 clips (24 fps) | ~12–15s | 0.0 (CPU) | $0.00 | $0.00 |
| `05_music` | Local Tizita Pentatonic Synthesizer | 1 track (95s) | ~1.5s | 0.0 (CPU) | $0.00 | $0.00 |
| `06_assemble` | Local FFmpeg (ducking, `-14 LUFS`, subtitles, end card) | 2 exports (`16:9` + `9:16`, 87.6s each) | ~10–15s | 0.0 (CPU) | $0.00 | $0.00 |
| **Total** | | **10 shots + 2 final films** | **~75–85s (cold)** | **0.0 local/cloud GPU min** | **~$0.036** | **$0.00** |

## Cost-Control & Efficiency Mechanisms
- **Content-Hash Caching:** Every stage writes a SHA-256 hash of its inputs into a companion `.json` file. Editing a single shot regenerates only that shot; all other stages hit `[CACHE]` at **$0.00** and **~0.0s** latency.
- **Zero-GPU Fallback:** Using local FFmpeg Ken Burns motion eliminated Kaggle T4 queue waits and kept GPU minutes at `0.0`, while keeping characters artifact-free.
- **Telemetry Auditing:** Every API call, fallback, latency, and cost estimate is logged to `runs.jsonl`.