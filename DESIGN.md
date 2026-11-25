# Design & Audience Notes

## Concept & Tone
- **Title:** A Christmas to Remember – Addis Ababa, 1975
- **Tone:** Warm, emotional, nostalgic, and slightly playful, told from the father's childhood perspective.

## Audience & Intent
- **Audience:** Family members, relatives at home and abroad, and peers watching on mobile phones (vertical `9:16`) or larger screens (horizontal `16:9`).
- **Intent:** Make viewers feel connected to 1975 Addis Ababa holiday warmth, community spirit, and family memories passed across generations.

---

## Shot-by-Shot Purpose (10 Shots)
Every shot in `storyboard.json` serves a specific narrative beat along the 1975 Christmas journey:

| Shot | Beat / Location | Purpose in the Story |
|---|---|---|
| **01** | Opening / Gotera Morning | Establishes the 1975 Addis Ababa setting and nostalgic holiday morning mood. |
| **02** | Family Preparation | Introduces the father's childhood perspective and excitement for Genna (Christmas). |
| **03** | Setting Out on Foot | Begins the physical journey across the city, grounding the viewer in the neighborhood. |
| **04** | Passing Meskel Square | Captures the scale and festive atmosphere of Addis Ababa in the mid-1970s. |
| **05** | UN ECA & Landmarks | Anchors the route with recognizable civic landmarks that older relatives immediately remember. |
| **06** | Parliament Area | Adds historical texture and shows the rhythm of the city streets on a holiday. |
| **07** | 4 Kilo Streets | Builds momentum and community energy as more people gather along the walk. |
| **08** | 6 Kilo Approach | Transitions from the busy streets toward the anticipation of the main gathering. |
| **09** | Arriving at Jan Meda | Delivers the emotional climax—the open field, crowds, and shared celebration. |
| **10** | Closing Reflection | Ties the 1975 memory back to the present day, leaving the audience with warmth and pride. |

---

## User Test 1: Radio Cut (Amharic Narration & Pacing)
- **Participants:** 3 reviewers (Father, Brother, Friend).
- **What they said:**
  - **Father:** Confirmed the story flow and landmark sequence felt authentic to 1975 Addis Ababa, but noted that a few transitions felt slightly rushed.
  - **Brother:** Liked the clarity of the Amharic narration and suggested leaving a brief pause between shots so each memory has room to land.
  - **Friend:** Said the emotional arc worked well even without visuals, and recommended keeping the background music gentle so it never competes with the voice.
- **Changes made to `storyboard.json` & pipeline:**
  - Slowed narration delivery slightly (`-5%` rate) for a calmer, storytelling cadence.
  - Updated `04_shots.py` to pad every shot by `+0.6s` beyond the measured audio length (`max(storyboard_dur, audio_dur + 0.6s)`) so narration never clips or rushes into the next shot.

---

## User Test 2: Near-Final Cut (`film_16x9.mp4` & `film_9x16.mp4`)
We screened the near-final `16:9` and `9:16` exports to 3 viewers to evaluate emotional resonance, Amharic clarity, subtitle readability, and audio balance.

| Reviewer | Relationship | Feedback on Story & Visuals | Audio & Subtitle Notes | Action Taken |
|---|---|---|---|---|
| **Reviewer 1** | Father | The 1975 Addis Ababa scenes felt warm and nostalgic. | Amharic voice is clear; subtitles are easy to read. | Kept current pacing and subtitle outline. |
| **Reviewer 2** | Brother | Liked the vertical `9:16` framing for mobile viewing. | Background music sits nicely under the voice. | Verified 3s AI end card plays with music swell. |
| **Reviewer 3** | Friend | Good pacing across the 10 shots. | Suggested checking end-card visibility at the very end. | Fixed `apad=pad_dur=3` and removed `-shortest` in `06_assemble.py` so the 3-second *"Made with AI"* card displays in full. |