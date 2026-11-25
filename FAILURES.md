\# Failures, Root Causes \& Fixes



Every major failure encountered during development is documented below along with its root cause and verified fix.



| # | Stage | Symptom / Error | Root Cause | Fix Applied |

|---|---|---|---|---|

| 1 | `02\_narration` | `400 INVALID\_ARGUMENT: Unknown name "speechConfig"` \& `503 UNAVAILABLE` | API schema mismatch on preview TTS endpoint and high-demand throttling on `gemini-3.8-flash`. | Added automatic fallback to `edge-tts` (`am-ET-AmehaNeural`) with full failure logging in `runs.jsonl`. |

| 2 | `03\_keyframes` | `400 Client Error: Bad Request` from Cloudflare Workers AI | `@cf/black-forest-labs/flux-1-schnell` only accepts `prompt` and `steps` (1–8); extra keys (`width`, `height`, `seed`, `num\_steps`) are rejected. | Simplified JSON payload to `{"prompt": ..., "steps": 4}` and added retry with backoff. |

| 3 | `06\_assemble` | `SyntaxError` on nested escaped quotes in f-string | Escaped quotes inside Python f-string expression on line 159. | Replaced inner double quotes with single quotes. |

| 4 | `06\_assemble` | FFmpeg exit status `4294967274` (`-22`) during `9:16` concat | Cropping and scaling `sub\_9x16.mp4` produced a different Sample Aspect Ratio (SAR) than `end\_9x16.mp4`. | Applied `setsar=1` to both `\[0:v]` and `\[1:v]` streams prior to `concat`. |

| 5 | `06\_assemble` | FFmpeg exit status `4294967274` (`-22`) in `make\_end\_card` | Unescaped colons (`:`) inside `drawtext` text string broke FFmpeg's filter argument parser. | Replaced colons with dashes (`Visuals - FLUX.1 Schnell \\| Voice - Edge-TTS \\| Assembly - FFmpeg`). |

| 6 | `06\_assemble` | 3-second \*"Made with AI"\* end card missing from final MP4s | `sidechaincompress` stopped at the end of narration (`84.6s`), and `-shortest` truncated the last 3 seconds of video. | Added `apad=pad\_dur=3` to the voice stream before sidechain compression and removed `-shortest`. |

| 7 | Verification | Final video appeared silent on first playback | Opened intermediate video-only file (`raw\_16x9.mp4` / `sub\_16x9.mp4`) instead of `film\_16x9.mp4`; also normalized mixed sample rates (`24 kHz mono` vs `44.1 kHz stereo`). | Verified audio presence via FFmpeg `volumedetect` (`-16.9 dB` mean volume) and forced `aformat=sample\_rates=44100:channel\_layouts=stereo` on both audio inputs. |

