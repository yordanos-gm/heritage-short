# Experiments & Iterations

Every major design and engineering choice in the pipeline was tested as a structured **Hypothesis → Change → Result → Decision** experiment and backed by `runs.jsonl` and FFmpeg verification logs.

---

## Experiment 1: Amharic Narration Engine Selection (Gemini TTS vs. `edge-tts`)
- **Hypothesis:** Gemini native TTS (`gemini-2.5-flash-preview-tts` / `gemini-3.8-flash`) would deliver warm, expressive Amharic narration directly through the `google-genai` SDK.
- **Change:** Tested `speechConfig` on the preview TTS endpoint and `gemini-3.8-flash` for Shot 01–10.
- **Result:** The preview endpoint rejected `speechConfig` (`400 INVALID_ARGUMENT`), and `gemini-3.8-flash` returned `503 UNAVAILABLE` under high traffic. Falling back to `edge-tts` (`am-ET-AmehaNeural`) succeeded on all 10 shots in ~25.5s total with clear Amharic pronunciation.
- **Decision:** Implemented a two-tier resilient narration stage: attempt Gemini first, log the failure in `runs.jsonl`, and automatically fall back to `edge-tts` (`am-ET-AmehaNeural`).

## Experiment 2: Narration Pacing & Speaking Rate
- **Hypothesis:** Default TTS speed (`+0%`) would feel slightly rushed for a nostalgic 1975 family memory.
- **Change:** Adjusted `edge-tts` speaking rate to `-5%` and added `+0.6s` breathing room per shot in `04_shots.py` (`max(storyboard_dur, audio_dur + 0.6s)`).
- **Result:** Total narration runtime settled at `84.6s` (inside the 60–90s target) with natural pauses between landmarks.
- **Decision:** Locked `-5%` speaking rate and `+0.6s` per-shot padding.

## Experiment 3: Cloudflare FLUX.1 Schnell API Payload Schema
- **Hypothesis:** Passing explicit `width=1280`, `height=720`, `seed`, and `num_steps` to `@cf/black-forest-labs/flux-1-schnell` would enforce widescreen framing and determinism.
- **Change:** Sent full parameter payload vs. minimal `{"prompt": ..., "steps": 4}` payload.
- **Result:** Extra parameters returned `400 Bad Request` because Cloudflare's endpoint only accepts `prompt` and `steps` (1–8, default 4). Minimal payload succeeded on all 11 images (reference sheet + 10 shots) in ~27s (~2.5s/image).
- **Decision:** Standardized on `{"prompt": ..., "steps": 4}` with retry + exponential backoff.

## Experiment 4: Visual Consistency Across 10 Shots
- **Hypothesis:** Generating a dedicated character/style reference sheet first and appending an identical 1975 `style_block` to every shot prompt would reduce visual drift across shots.
- **Change:** Added `reference_sheet.png` generation and injected a shared `style_block` + `subject centered in frame` into all 10 keyframe prompts.
- **Result:** Warm 1975 Addis Ababa color palette, film grain, and clothing style stayed cohesive across all 10 shots, and centered subjects survived the `9:16` vertical center-crop cleanly.
- **Decision:** Kept the shared `style_block` and centered-framing rule inside `storyboard.json`.

## Experiment 5: Motion Generation (Local FFmpeg Ken Burns vs. Cloud GPU Queue)
- **Hypothesis:** Slow, alternating FFmpeg `zoompan` (Ken Burns) motion matched to each shot's exact audio duration would avoid GPU queue bottlenecks while keeping characters artifact-free.
- **Change:** Configured `04_shots.py` to probe each narration MP3 and apply alternating gentle zoom-in / zoom-out pans at 24 fps.
- **Result:** All 10 moving clips rendered locally in seconds with zero face morphing, zero flicker, and exact audio-to-video duration alignment.
- **Decision:** Adopted audio-matched FFmpeg `zoompan` as the deterministic motion stage.

## Experiment 6: Content-Hash Caching & Partial Regeneration
- **Hypothesis:** Storing a SHA-256 hash of each stage's inputs in companion `.json` metadata files would let `python run.py` skip unchanged assets on reruns.
- **Change:** Added `compute_hash()` and cache checks in `02_narration.py`, `03_keyframes.py`, `04_shots.py`, and `05_music.py`.
- **Result:** Full rerun of `python run.py` hit `[CACHE]` on all 10 narration clips, 11 keyframes, 10 motion clips, and the score—making 0 API calls and completing assembly cleanly.
- **Decision:** Kept content-hash caching enabled across all generative stages.

## Experiment 7: Audio Sample-Rate & Channel Normalization Before Mixing
- **Hypothesis:** Mixing `24 kHz mono` narration (`edge-tts` MP3) directly with `44.1 kHz stereo` background music could cause silent or mismatched audio streams in FFmpeg `sidechaincompress`.
- **Change:** Inserted `aformat=sample_rates=44100:channel_layouts=stereo` on both `[0:a]` (voice) and `[1:a]` (music) prior to sidechain ducking, and verified output with FFmpeg `volumedetect`.
- **Result:** `volumedetect` confirmed clean `44100 Hz` stereo AAC (`192 kbps`) at `-16.9 dB` mean volume in `film_16x9.mp4` and `film_9x16.mp4` (`shot_01.mp3` measured `-26.1 dB` pre-mix).
- **Decision:** Locked explicit `aformat` normalization on both audio inputs before mixing.

## Experiment 8: Sidechain Ducking & 3-Second "Made with AI" End-Card Timing
- **Hypothesis:** Using `amix=duration=first` with `-shortest` would automatically trim the looping score to match the video length.
- **Change:** Compared `duration=first` + `-shortest` against padding the voice stream with 3 seconds of silence (`apad=pad_dur=3`), `duration=longest`, and removing `-shortest`.
- **Result:** With `-shortest`, `sidechaincompress` stopped at `84.6s` (end of voice) and chopped off the 3-second *"Made with AI"* end card. With `apad=pad_dur=3` and `-shortest` removed, the full `87.6s` film exported cleanly with the music swelling smoothly under the 3-second end card.
- **Decision:** Kept `apad=pad_dur=3` + `duration=longest` without `-shortest`.

## Experiment 9: Dual Aspect-Ratio (`9:16`) Concat SAR Alignment
- **Hypothesis:** Appending `end_9x16.mp4` directly to the cropped `sub_9x16.mp4` would concatenate cleanly.
- **Change:** Added `setsar=1` to both `[0:v]` and `[1:v]` streams before `concat` in `06_assemble.py`.
- **Result:** Without `setsar=1`, FFmpeg exited with status `4294967274` (`-22`) due to mismatched Sample Aspect Ratios. With `setsar=1`, `film_9x16.mp4` exported without error.
- **Decision:** Enforced `setsar=1` on both streams prior to concatenation.

## Experiment 10: FFmpeg `drawtext` End-Card Formatting
- **Hypothesis:** Listing the AI stack with colons (`Visuals: FLUX.1 Schnell | Voice: Edge-TTS | Assembly: FFmpeg`) inside FFmpeg `drawtext` would render cleanly on the end card.
- **Change:** Replaced unescaped colons with dashes (`Visuals - FLUX.1 Schnell | Voice - Edge-TTS | Assembly - FFmpeg`).
- **Result:** Unescaped colons broke FFmpeg's filter argument parser (exit status `4294967274`). Dash separators rendered cleanly on both `1280x720` and `720x1280` end cards.
- **Decision:** Standardized on dash separators in `make_end_card()`.

---

## Experiment 11 (Ceiling): Multilingual Horn of Africa TTS Audit (Somali, Tigrinya, Afaan Oromo)
- **Hypothesis:** `edge-tts` (our free-tier narration engine) would support other major Ethiopian and Horn of Africa languages—Somali, Tigrinya, and Afaan Oromo—at comparable quality to Amharic (`am-ET-AmehaNeural`).
- **Change:** Built `ceiling_lang_test.py` to query `edge-tts.list_voices()` for `am-`, `so-`, `om-`, and `ti-` locales, then synthesized Shot 01 in Somali (`so-SO-MuuseNeural`), Tigrinya (cross-lingual via `am-ET-AmehaNeural`), and Afaan Oromo (cross-lingual via `so-SO-MuuseNeural`), logging exact latencies to `runs.jsonl`.
- **Result:**
  - **Voice Availability:** `edge-tts` provides native neural voices for **Amharic** (`am-ET-AmehaNeural`, `am-ET-MekdesNeural`) and **Somali** (`so-SO-MuuseNeural`, `so-SO-UbaxNeural`), but no native voices for **Afaan Oromo (`om-`)** or **Tigrinya (`ti-`)**.
  - **Somali (`shot01_somali.mp3`):** Generated in `17.93s`; natural prosody and clear pronunciation, making it viable for multilingual pipeline expansion.
  - **Tigrinya via Amharic (`shot01_tigrinya_via_amharic.mp3`):** Generated in `18.2s`; intelligible because of shared Ge'ez script, though it flattens Tigrinya-specific pharyngeal sounds and uses Amharic cadence.
  - **Afaan Oromo via Somali (`shot01_oromo_via_somali.mp3`):** Generated in `18.32s`; struggles with Oromo-specific phonology (`yy`, `q`, vowel length), showing that cross-lingual fallback is not production-ready for Afaan Oromo.
- **Decision / Insight:** Free-tier `edge-tts` can expand this pipeline to **Somali**, while **Tigrinya** and **Afaan Oromo** require dedicated regional TTS models or Gemini TTS once free-tier `503` throttling stabilizes.

