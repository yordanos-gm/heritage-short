\# Heritage Short: A Christmas to Remember – Addis Ababa, 1975



An automated, cache-aware, multi-model AI video pipeline that turns a structured JSON storyboard into dual-format (\*\*16:9\*\* horizontal and \*\*9:16\*\* vertical) heritage short films with Amharic narration, English subtitles, Ethiopian Tizita-inspired background music, and a 3-second AI disclosure end card.



\## Features

\- \*\*One-Command Execution:\*\* Run the entire 6-stage pipeline with `python run.py`.

\- \*\*Content-Hash Caching:\*\* Skips unchanged narration, keyframes, video clips, and music on reruns—zero wasted API calls.

\- \*\*Resilient TTS Fallback:\*\* Attempts Gemini TTS first and automatically falls back to native Amharic neural speech (`edge-tts` / `am-ET-AmehaNeural`) on `400`/`503` API errors.

\- \*\*Broadcast-Ready Audio:\*\* Automatic sidechain ducking of background music under narration and `-14 LUFS` loudness normalization.

\- \*\*Dual-Aspect Exports:\*\* Produces both `1280x720` (`16:9`) and `720x1280` (`9:16`) MP4s with safe-area burned-in subtitles and a 3-second \*"Made with AI"\* end card.

\- \*\*Run Telemetry:\*\* Every stage logs model, parameters, seed, latency, cache status, and cost to `runs.jsonl`.



\## Project Structure

```text

heritage-short/

├── run.py                  # One-command pipeline orchestrator

├── storyboard.json         # 10-shot story spec (Amharic narration, EN subtitles, visual prompts)

├── .env                    # API keys (ignored by Git)

├── .env.example            # Safe template for required environment variables

├── runs.jsonl              # Structured execution \& latency log

├── pipeline/

│   ├── utils.py            # Hashing, caching, directory \& logging helpers

│   ├── 01\_validate.py      # Storyboard schema \& duration validation

│   ├── 02\_narration.py     # Amharic TTS (Gemini primary + edge-tts fallback)

│   ├── 03\_keyframes.py     # Character reference sheet + 10 keyframes (FLUX.1 Schnell)

│   ├── 04\_shots.py         # Audio-matched Ken Burns motion clips (FFmpeg)

│   ├── 05\_music.py         # Tizita pentatonic underscore synthesizer (or custom MP3)

│   └── 06\_assemble.py      # Subtitle burn-in, sidechain ducking, end card \& 16:9/9:16 export

└── outputs/

&#x20;   ├── narration/          # Per-shot Amharic audio + cache metadata

&#x20;   ├── keyframes/          # Reference sheet + 10 generated stills

&#x20;   ├── shots/              # 10 rendered moving clips

&#x20;   ├── music/              # Background score

&#x20;   └── final/              # film\_16x9.mp4, film\_9x16.mp4, subtitles.srt

