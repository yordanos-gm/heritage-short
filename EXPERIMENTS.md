\---



\## 3. `EXPERIMENTS.md`



```markdown

\# Experiments \& Iterations



\## Experiment 1: Amharic Narration Engine Selection

\- \*\*Hypothesis:\*\* Gemini native audio output (`gemini-2.5-flash-preview-tts` / `gemini-3.8-flash`) would provide expressive, warm Amharic narration directly via the `google-genai` SDK.

\- \*\*Result:\*\* The preview TTS endpoint rejected `speechConfig` (`400 INVALID\_ARGUMENT`), and `gemini-3.8-flash` returned `503 UNAVAILABLE` under high traffic.

\- \*\*Decision:\*\* Implemented a resilient two-tier architecture—attempt Gemini first, log the failure, and automatically fall back to `edge-tts` (`am-ET-AmehaNeural` at `-5%` speaking rate). All 10 shots generated in \~25.5s total with clear, natural Amharic pronunciation.



\## Experiment 2: Keyframe Generation Parameters (Cloudflare FLUX.1 Schnell)

\- \*\*Hypothesis:\*\* Passing explicit `width=1280`, `height=720`, `seed`, and `num\_steps` would lock framing and determinism.

\- \*\*Result:\*\* Cloudflare's `@cf/black-forest-labs/flux-1-schnell` endpoint returned `400 Bad Request` on extra parameters.

\- \*\*Decision:\*\* Stripped payload to the supported schema (`prompt`, `steps=4`) and enforced framing via prompt engineering (`subject centered in frame` + shared `style\_block`). All 11 images (reference sheet + 10 shots) generated in \~27s (\~2.5s/image).



\## Experiment 3: Audio Ducking \& End-Card Timing

\- \*\*Hypothesis:\*\* Using `amix=duration=first` with `-shortest` would cleanly trim the looping background score to match the film.

\- \*\*Result:\*\* `sidechaincompress` terminated when the voice ended at `84.6s`, causing `-shortest` to chop off the 3-second \*"Made with AI"\* end card.

\- \*\*Decision:\*\* Added `apad=pad\_dur=3` to the voice stream before sidechain compression and removed `-shortest`. The final film now runs `87.6s` with music swelling smoothly over the 3-second end card.

