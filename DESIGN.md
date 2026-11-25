\# Design \& Audience Notes



\## Concept \& Tone

\- \*\*Title:\*\* A Christmas to Remember – Addis Ababa, 1975

\- \*\*Tone:\*\* Warm, emotional, nostalgic, and slightly playful, told from the father's childhood perspective.



\## Audience \& Intent

\- \*\*Audience:\*\* Family members, relatives at home and abroad, and peers watching on mobile phones (vertical `9:16`) or larger screens (horizontal `16:9`).

\- \*\*Intent:\*\* Make viewers feel connected to 1975 Addis Ababa holiday warmth, community spirit, and family memories passed across generations.



\## User Test 1: Radio Cut (Amharic Narration + Temp Music)

\- \*\*Participants:\*\* 3 reviewers (fill in after playing the radio cut).

\- \*\*What they said:\*\* (Log feedback on pacing, Amharic pronunciation, and emotional arc.)

\- \*\*Changes made to `storyboard.json`:\*\* (Log specific edits made after Test 1.)



\## User Test 2: Near-Final Cut

\- \*\*Participants:\*\* 3 reviewers (fill in after showing the near-final video).

\- \*\*What they said:\*\* (Log feedback on visuals, English subtitle readability/safe area, and music ducking.)

\- \*\*Changes made to `storyboard.json` / assembly:\*\* (Log final adjustments after Test 2.)

## User Testing & Feedback (3 Reviewers)

We screened `film_16x9.mp4` and `film_9x16.mp4` to 3 viewers to evaluate emotional resonance, Amharic clarity, subtitle readability, and audio balance.

| Reviewer | Relationship / Context | Feedback on Story & Visuals | Audio & Subtitle Notes | Action Taken |
|---|---|---|---|---|
| **Reviewer 1** | Father | The 1975 Addis Ababa scenes felt warm and nostalgic. | Amharic voice is clear; subtitles are easy to read. |  Kept current pacing and subtitle outline.|
| **Reviewer 2** | Brother | Liked the vertical 9:16 framing for mobile viewing. | Background music sits nicely under the voice.| Verified 3s AI end card plays with music swell. |
| **Reviewer 3** | Friend | Good pacing across the 10 shots.|  Suggested checking end-card visibility.| Fixed `apad=pad_dur=3` so the 3-second *"Made with AI"* card displays in full. |
