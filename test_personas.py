#!/usr/bin/env python3
"""
Interactive Persona Voice Audition Script for mcp-speak.
Allows testing and previewing different persona voices using OmniVoice or macOS 'say'.
"""

import os
import sys
import argparse
import tempfile
import subprocess
from pathlib import Path

# Auto-re-execute using .venv python if available and not already inside a virtualenv
PROJECT_DIR = Path(__file__).parent.resolve()
VENV_PYTHON = PROJECT_DIR / ".venv" / "bin" / "python"
if sys.prefix == sys.base_prefix and VENV_PYTHON.exists():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)

from speak_server import load_config, OmniVoiceEngine, SayEngine

SAMPLE_PHRASES = {
    "agent_smith": "Hear that, Mister Erfan? That is the sound of inevitability. It is the sound of your code compiling.",
    "tech_priest": "Praise the Omnissiah. The sacred scripts have been executed without violation to the Machine Spirit.",
    "sarcastic_senior": "Oh look, another commit that somehow didn't break production. Don't let it go to your head.",
    "over_eager_intern": "Everything worked on the very first try! That was totally incredible! What should we build next?!",
    "existential_emo": "The build passed, but what does it really matter? We're all just delaying the inevitable segmentation fault.",
    "pun_master": "I tried writing a script for a bakery, but I couldn't get enough dough. Don't worry, my Python is much sharper.",
    "poet": "Once upon a midnight dreary, while I pondered weak and weary, all the bugs have flown away, errors cease till dawn of day.",
    "nature_narrator": "Here, in the dense undergrowth of the repository, we observe the developer in their natural habitat, carefully crafting a new branch.",
    "head_chef": "Look at this spaghetti code! It's so raw the server is still trying to compile the comments! Wake up and refactor it now!",
    "neutral_mainframe": "Instruction received and processed. Operation status: nominal. Awaiting next command.",
}


def get_persona_voice_mode(persona_key: str, config: dict) -> str:
    """Return a descriptive string of how this persona will be synthesized (Clone vs Design)."""
    voices_dir = Path(config.get("voices_dir", "voices"))
    if not voices_dir.is_absolute():
        voices_dir = PROJECT_DIR / voices_dir

    wav_file = voices_dir / f"{persona_key}.wav"
    pt_file = voices_dir / f"{persona_key}.pt"
    txt_file = voices_dir / f"{persona_key}.txt"

    if pt_file.exists():
        return f"Cached Clone ({pt_file.name})"
    elif wav_file.exists():
        has_txt = " + transcript" if txt_file.exists() else " (auto ASR)"
        return f"Cloned Audio ({wav_file.name}{has_txt})"
    else:
        voice_designs = config.get("voice_designs", {})
        persona_cfg = voice_designs.get(persona_key, {})
        instruct = persona_cfg.get("instruct", "default voice")
        return f"Voice Design ({instruct})"


def play_persona_sample(
    persona_key: str,
    engine_type: str,
    custom_text: str = None,
    custom_voice_file: str = None,
):
    config = load_config()
    config["engine"] = engine_type
    config["persona"] = persona_key

    text = custom_text if custom_text else SAMPLE_PHRASES.get(persona_key, "Hello! This is a voice test.")

    if custom_voice_file:
        voice_mode = f"Custom Audio ({custom_voice_file})"
    elif engine_type == "omnivoice":
        voice_mode = get_persona_voice_mode(persona_key, config)
    else:
        voice_mode = "macOS native say"

    print("\n" + "=" * 60)
    print(f"🎙️  Persona:  {persona_key.upper()}")
    print(f"⚙️  Engine:   {engine_type.upper()}")
    print(f"🎨 Voice:    {voice_mode}")
    print(f"💬 Message:  \"{text}\"")
    print("=" * 60)
    print("Generating and playing speech...")

    if engine_type == "omnivoice":
        engine = OmniVoiceEngine(config)
        if custom_voice_file:
            # Dynamically override clone prompt for custom voice file audition
            model = engine._get_model()
            prompt = model.create_voice_clone_prompt(ref_audio=custom_voice_file)
            engine._voice_clone_prompts[persona_key] = prompt
    else:
        engine = SayEngine()

    engine.speak(text)
    print("✓ Finished playback.\n")


def interactive_menu(engine_type: str):
    config = load_config()
    persona_keys = list(SAMPLE_PHRASES.keys())

    while True:
        print("\n" + "=" * 50)
        print("        🎙️  Persona Voice Audition Menu  🎙️        ")
        print("=" * 50)
        print(f"Current Engine: {engine_type.upper()}\n")

        for idx, key in enumerate(persona_keys, start=1):
            mode_desc = get_persona_voice_mode(key, config)
            clone_badge = " [CLONED]" if "Clone" in mode_desc else ""
            print(f"  [{idx}] {key.replace('_', ' ').title():<20}{clone_badge} ({mode_desc})")

        print(f"  [A] Play All Personas Sequentially")
        print(f"  [T] Toggle Engine (OmniVoice / Say)")
        print(f"  [Q] Quit")

        choice = input(f"\nSelect persona [1-{len(persona_keys)}, A, T, Q]: ").strip().lower()

        if choice in ["q", "exit"]:
            print("Exiting audition.")
            break
        elif choice == "t":
            engine_type = "say" if engine_type == "omnivoice" else "omnivoice"
            print(f"Switched engine to: {engine_type.upper()}")
        elif choice == "a":
            for key in persona_keys:
                play_persona_sample(key, engine_type)
        elif choice.isdigit() and 1 <= int(choice) <= len(persona_keys):
            selected_key = persona_keys[int(choice) - 1]
            custom_msg = input("\nEnter custom text (or press Enter to use default sample): ").strip()
            play_persona_sample(selected_key, engine_type, custom_msg if custom_msg else None)
        else:
            print("Invalid selection. Please try again.")


def main():
    parser = argparse.ArgumentParser(description="Audition persona voices for mcp-speak.")
    parser.add_argument("--persona", choices=list(SAMPLE_PHRASES.keys()), help="Directly test a specific persona")
    parser.add_argument("--all", action="store_true", help="Play samples for all personas sequentially")
    parser.add_argument("--engine", choices=["omnivoice", "say"], default="omnivoice", help="TTS Engine to test with")
    parser.add_argument("--voice-file", help="Path to custom reference WAV audio file for voice cloning")
    parser.add_argument("--text", help="Custom text to speak")
    args = parser.parse_args()

    if args.all:
        for key in SAMPLE_PHRASES.keys():
            play_persona_sample(key, args.engine, args.text, args.voice_file)
    elif args.persona:
        play_persona_sample(args.persona, args.engine, args.text, args.voice_file)
    else:
        interactive_menu(args.engine)


if __name__ == "__main__":
    main()

