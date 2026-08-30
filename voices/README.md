# Persona Reference Audio Directory (`voices/`)

Place `.wav` reference audio recordings in this directory to enable **Neural Voice Cloning** for any persona.

## How It Works

When `mcp-speak` is configured with `engine: "omnivoice"`:
1. **Cloned Voice Check**: The server looks for a matching `.wav` file for the active persona (e.g., `voices/pun_master.wav` for the `pun_master` persona).
2. **Clone Synthesis**: If found, OmniVoice extracts the vocal timbre and characteristics from the audio clip to generate speech matching that exact voice.
3. **Graceful Fallback**: If no `.wav` file is present for a persona, the server seamlessly falls back to instruction-based Voice Design (e.g. pitch, speed, and accent instructions).

---

## File Naming Convention

| Persona Name | Reference Audio File | Optional Transcript File |
|---|---|---|
| `agent_smith` | `agent_smith.wav` | `agent_smith.txt` |
| `pun_master` | `pun_master.wav` | `pun_master.txt` |
| `nature_narrator` | `nature_narrator.wav` | `nature_narrator.txt` |
| `tech_priest` | `tech_priest.wav` | `tech_priest.txt` |
| `sarcastic_senior` | `sarcastic_senior.wav` | `sarcastic_senior.txt` |
| `over_eager_intern` | `over_eager_intern.wav` | `over_eager_intern.txt` |
| `existential_emo` | `existential_emo.wav` | `existential_emo.txt` |
| `poet` | `poet.wav` | `poet.txt` |
| `head_chef` | `head_chef.wav` | `head_chef.txt` |
| `neutral_mainframe` | `neutral_mainframe.wav` | `neutral_mainframe.txt` |

---

## Audio Recommendations

- **Format:** Uncompressed WAV (`.wav`).
- **Duration:** 3 to 10 seconds of clear, uninterrupted speech is ideal. (Audio clips longer than 20 seconds are automatically trimmed by OmniVoice).
- **Quality:** High signal-to-noise ratio, clean microphone recording without background music or heavy reverb.
- **Sample Rate:** Any standard sample rate (e.g. 24kHz, 44.1kHz, 48kHz) — OmniVoice resamples to 24kHz internally.

---

## Optional Transcript (`.txt`) for Faster Startup

If you place a `.txt` file with the exact transcript alongside the `.wav` file (e.g., `pun_master.txt`), OmniVoice uses the text directly and **does not need to download or load the Whisper ASR model**.

If no `.txt` file is found, OmniVoice will automatically transcribe the audio using Whisper ASR on the fly.
