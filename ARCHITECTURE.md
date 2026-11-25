\---



\## 2. `ARCHITECTURE.md`



```markdown

\# System Architecture



\## Pipeline Data Flow

```text

storyboard.json

&#x20;     │

&#x20;     ▼

\[01\_validate] ──► Validates schema, 10 shots, and target runtime

&#x20;     │

&#x20;     ├──► \[02\_narration] ──► Gemini TTS ──(fallback on 400/503)──► edge-tts (am-ET-AmehaNeural)

&#x20;     │         │                                                        │

&#x20;     │         └──────────────────► outputs/narration/shot\_XX.mp3 ◄─────┘

&#x20;     │

&#x20;     ├──► \[03\_keyframes] ──► Cloudflare FLUX.1 Schnell (4 steps)

&#x20;     │         │             Generates reference\_sheet.png + shot\_01..10.png

&#x20;     │         └──────────────────► outputs/keyframes/

&#x20;     │

&#x20;     ├──► \[04\_shots] ──────► FFmpeg (imageio-ffmpeg)

&#x20;     │         │             Probes narration duration + 0.6s pad; applies alternating zoompan

&#x20;     │         └──────────────────► outputs/shots/shot\_XX.mp4

&#x20;     │

&#x20;     ├──► \[05\_music] ──────► Tizita Pentatonic Synth (or optional outputs/music/acestep\_score.mp3)

&#x20;     │         └──────────────────► outputs/music/score.wav

&#x20;     │

&#x20;     ▼

\[06\_assemble] ──► Syncs narration, ducks music (sidechaincompress), normalizes (-14 LUFS),

&#x20;                 burns English SRT subtitles, appends 3s "Made with AI" end card

&#x20;     │

&#x20;     ├──► outputs/final/film\_16x9.mp4 (1280x720, 87.6s)

&#x20;     └──► outputs/final/film\_9x16.mp4 (720x1280, 87.6s)

