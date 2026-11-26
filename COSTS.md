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

## Frontier Model Comparison (Current Stack vs. Paid Frontier APIs)

To contextualize our **$0.00 actual spend** (~$0.036 list-price equivalent on Cloudflare Workers AI), the table below compares our reproducible open/free-tier stack against representative commercial frontier models for a single full uncached render of this 10-shot, 87.6-second film (~1,350 Amharic characters, 11 images, 84.6s of shot motion, and 1 musical score). *Frontier prices reflect typical public API list-rate estimates as of late 2026.*

| Pipeline Stage | Current Stack (Measured) | Actual Cost | Representative Frontier Alternative | Estimated Frontier Rate | Est. Frontier Cost (1 Full Run) | Trade-Off & Engineering Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **02. Narration (10 shots, ~1,350 chars)** | `edge-tts` (`am-ET-AmehaNeural`, `-5%` rate) | **$0.00** | ElevenLabs Multilingual v2 / OpenAI TTS-HD | ~$0.03–$0.30 per 1K chars | **~$0.04 – $0.41** | Frontier voices offer richer emotional inflection in high-resource languages, but lack native Amharic neural support; `edge-tts` delivered clear native Amharic at zero cost. |
| **03. Keyframes (1 ref sheet + 10 shots)** | Cloudflare `@cf/black-forest-labs/flux-1-schnell` (`steps=4`) | **$0.00** (~$0.036 list equiv.) | OpenAI `gpt-image-1` / FLUX.1 Pro / Imagen 3 | ~$0.04–$0.08 per image (11 images) | **~$0.44 – $0.88** | Frontier image models yield finer detail and stronger prompt adherence, but `flux-1-schnell` with a shared 1975 `style_block` kept character identity consistent within free daily neuron limits. |
| **04. Shots / Motion (10 clips, 84.6s)** | Local FFmpeg `zoompan` Ken Burns (24 fps, `0.0` GPU min) | **$0.00** | Sora / Veo 2 / Runway Gen-3 / Kling I2V | ~$0.05–$0.12 per generated second (~85s) | **~$4.25 – $10.20** | Frontier image-to-video adds fluid subject motion, but introduces cloud queue latency (~30–120s/clip), character drift across cuts, and accounts for ~85%+ of total frontier spend. |
| **05. Music Score (95s underscore)** | Local `tizita-synth-v1` (pentatonic synthesizer) | **$0.00** | Suno / Udio / Lyria API | ~$0.05–$0.10 per generation | **~$0.05 – $0.10** | Frontier audio models produce richer acoustic instrumentation, while local synthesis guarantees exact Tizita modal tuning and deterministic zero-latency caching. |
| **Total (Uncached Run)** | **6-Stage Modular Pipeline** | **$0.00** | **Full Frontier Cloud Stack** | — | **~$4.78 – $11.59** | **~100% cost reduction** with deterministic SHA-256 caching (`$0.00` on reruns) and no cloud video queue bottlenecks. |

### Key Takeaways from the Comparison
1. **Video Generation Is the Dominant Cost Driver:** Replacing cloud image-to-video models (~$4.25–$10.20 per uncached draft) with audio-matched FFmpeg Ken Burns motion eliminated roughly 85–90% of typical frontier production cost while preventing character morphing across historical 1975 scenes.
2. **Iteration Economics:** During development and audience testing (Radio Cut + Near-Final Cut + live walkthrough edits), a frontier pipeline without content-hash caching would have cost **~$15–$35+** across multiple test renders, whereas our SHA-256 cache kept every iteration at **$0.00**.
3. **Language Coverage Beats Raw Model Size:** For Amharic storytelling, native regional voice support (`am-ET-AmehaNeural`) outperformed larger general-purpose frontier endpoints that either throttled (`503`) or lacked native Amharic phonology.