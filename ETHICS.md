\# Ethics, Consent, Licences \& AI Disclosure



\## Consent Record

\- \*\*Story \& Perspective:\*\* Based on a family memory of Christmas around 1975 in Addis Ababa (from Gotera to Jan Meda via 4 Kilo, 6 Kilo, Parliament, Meskel Square, and UN ECA), told from the father's childhood perspective.

\- \*\*Likeness \& Voice Consent:\*\* Explicit informed consent from family members regarding the family story is recorded prior to publication. No real individual's photograph or cloned voice is used; all visuals and narration are synthetic AI depictions.



\## Model \& Tool Licences

\- \*\*Narration (Gemini TTS / Gemini API):\*\* Subject to Google Gemini API terms; AI-generated audio disclosed.

\- \*\*Keyframes (FLUX via Cloudflare Workers AI):\*\* Specific model variant logged in `runs.jsonl` and `COSTS.md` (`FLUX.1 schnell` / `FLUX.2 klein 4B` Apache 2.0 vs. other variants).

\- \*\*Moving Shots (Wan 2.2):\*\* Apache 2.0 open-weight licence.

\- \*\*Music (ACE-Step 1.5):\*\* MIT licence; outputs usable per model terms.

\- \*\*Video Assembly \& Subtitles (FFmpeg):\*\* Open-source FFmpeg.



\## Labelling \& Provenance Plan

\- Toggle on the platform's AI-generated content disclosure label when uploading the `9:16` film.

\- Include an explicit AI end card at the end of both `9:16` and `16:9` exports.

\- Log every model call, seed, latency, and cost estimate in `runs.jsonl`.

# Ethics, Consent, Licences & AI Disclosure

## Consent Record
- **Story & Perspective:** Based on a family memory of Christmas around 1975 in Addis Ababa (from Gotera to Jan Meda via 4 Kilo, 6 Kilo, Parliament, Meskel Square, and UN ECA), told from the father's childhood perspective.
- **Likeness & Voice Consent:** Explicit informed consent from family members regarding the family story was recorded prior to publication. No real individual's photograph, likeness, or cloned voice is used; all visuals and narration are synthetic AI depictions.
- **Private Data:** Personal/identifying family details (full names, private addresses) were kept out of external free-tier API prompts.

## Model & Tool Licences (Actual Pipeline Stack)
- **Narration (Primary: Gemini 3.8 Flash TTS; Fallback: `edge-tts` / `am-ET-AmehaNeural`):** Subject to Google Gemini API terms and Microsoft Edge online TTS service terms; synthetic AI voice is disclosed.
- **Keyframes (`@cf/black-forest-labs/flux-1-schnell` via Cloudflare Workers AI):** Apache 2.0 licence (Black Forest Labs); executed under Cloudflare Workers AI free-tier terms.
- **Moving Shots (FFmpeg `zoompan` Ken Burns via `imageio-ffmpeg`):** Open-source FFmpeg (LGPL/GPL); deterministic local rendering.
- **Music (Local Tizita Pentatonic Synthesizer in `05_music.py`):** Custom Python-generated audio (original/unencumbered). *(Optional support for ACE-Step 1.5, MIT licence, is documented in the pipeline.)*
- **Video Assembly & Subtitles (FFmpeg):** Open-source FFmpeg.

## Labelling & Provenance Plan
- Toggle on the platform's AI-generated content disclosure label when publishing the film.
- Include an explicit 3-second **"Made with AI"** end card listing the tools used at the end of both `9:16` and `16:9` exports.
- Preserve provenance metadata and log every model call, fallback, latency, and cost estimate in `runs.jsonl`.

