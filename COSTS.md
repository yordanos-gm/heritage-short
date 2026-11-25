\# Cost Breakdown \& Efficiency Report



\## Total Production Cost: \*\*$0.00\*\*



| Stage | Provider / Engine | Usage (10 Shots) | Unit Cost | Actual Spend |

|---|---|---|---|---|

| Validation | Local Python (`01\_validate.py`) | 1 run | $0.00 | $0.00 |

| Narration | Gemini 3.8 Flash (primary) + `edge-tts` (`am-ET-AmehaNeural` fallback) | 10 clips (\~84.6s) | $0.00 | $0.00 |

| Keyframes | Cloudflare Workers AI (`@cf/black-forest-labs/flux-1-schnell`) | 11 images (ref + 10 shots, 4 steps) | Free tier (10,000 neurons/day) | $0.00 |

| Motion Clips | Local FFmpeg (`imageio-ffmpeg`) | 10 clips | $0.00 | $0.00 |

| Music | Local Tizita Pentatonic Synthesizer (`05\_music.py`) | 1 track (95s) | $0.00 | $0.00 |

| Final Assembly | Local FFmpeg (`06\_assemble.py`) | 2 exports (`16:9` + `9:16`) | $0.00 | $0.00 |

| \*\*Total\*\* | | | | \*\*$0.00\*\* |



\## Cost-Control Mechanisms

\- \*\*Content-Hash Caching:\*\* Rerunning `python run.py` after editing a single shot only regenerates that shot; all other stages hit `\[CACHE]` at \*\*$0.00\*\* and \*\*\~0.0s\*\* latency.

\- \*\*Telemetry Auditing:\*\* Every API and local call records `estimated\_cost\_usd`, `latency\_sec`, and `cached` status in `runs.jsonl`.

