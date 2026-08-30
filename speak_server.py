# /// script
# dependencies = [
#   "mcp",
#   "torch",
#   "torchaudio",
#   "omnivoice",
#   "soundfile",
# ]
# ///

import os
import sys
import re
import json
import queue
import tempfile
import threading
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

from mcp.server.fastmcp import FastMCP

SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = SCRIPT_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "engine": "omnivoice",
    "persona": "agent_smith",
    "device": "auto",
    "fallback_to_say": True,
    "voice_designs": {
        "agent_smith": {
            "instruct": "male, middle-aged, low pitch, american accent",
            "speed": 1.0,
        },
        "tech_priest": {
            "instruct": "male, elderly, very low pitch, british accent",
            "speed": 0.95,
        },
        "sarcastic_senior": {
            "instruct": "male, middle-aged, low pitch, american accent",
            "speed": 1.0,
        },
        "over_eager_intern": {
            "instruct": "female, young adult, high pitch, american accent",
            "speed": 1.1,
        },
        "existential_emo": {
            "instruct": "male, teenager, low pitch, american accent",
            "speed": 0.8,
        },
        "pun_master": {
            "instruct": "male, middle-aged, moderate pitch, american accent",
            "speed": 1.05,
        },
        "poet": {
            "instruct": "male, middle-aged, low pitch, british accent",
            "speed": 0.95,
        },
        "nature_narrator": {
            "instruct": "male, elderly, very low pitch, british accent",
            "speed": 0.95,
        },
        "head_chef": {
            "instruct": "male, middle-aged, moderate pitch, british accent",
            "speed": 1.1,
        },
        "neutral_mainframe": {
            "instruct": "male, young adult, moderate pitch, russian accent",
            "speed": 1.0,
        },
    },
}


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json with fallback to defaults and env vars."""
    config = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                config.update(user_config)
        except Exception as e:
            print(f"[mcp-speak] Warning: Failed to read {CONFIG_FILE}: {e}", file=sys.stderr)

    # Environment variable overrides
    if "MCP_SPEAK_ENGINE" in os.environ:
        config["engine"] = os.environ["MCP_SPEAK_ENGINE"].strip().lower()
    if "MCP_SPEAK_PERSONA" in os.environ:
        config["persona"] = os.environ["MCP_SPEAK_PERSONA"].strip().lower()
    if "MCP_SPEAK_DEVICE" in os.environ:
        config["device"] = os.environ["MCP_SPEAK_DEVICE"].strip().lower()

    return config


class SayEngine:
    """Fallback TTS engine using native macOS 'say' command."""

    def speak(self, message: str) -> None:
        subprocess.run(["say", message], check=True)


class OmniVoiceEngine:
    """Neural TTS engine using OmniVoice with zero-shot Voice Design and pipelined streaming."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.device = None
        self._lock = threading.Lock()
        self._fallback_say = SayEngine()

    def _resolve_device(self) -> str:
        req_dev = self.config.get("device", "auto").lower()
        if req_dev != "auto":
            return req_dev

        import torch

        if torch.cuda.is_available():
            return "cuda:0"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _get_model(self):
        if self.model is not None:
            return self.model

        with self._lock:
            if self.model is None:
                from omnivoice import OmniVoice

                self.device = self._resolve_device()
                print(f"[mcp-speak] Initializing OmniVoice on device '{self.device}'...", file=sys.stderr)
                self.model = OmniVoice.from_pretrained(
                    "k2-fsa/OmniVoice",
                    device_map=self.device,
                )
                print("[mcp-speak] OmniVoice model loaded successfully.", file=sys.stderr)
        return self.model

    def _synthesize_to_file(self, text: str, instruct: str, speed: float) -> str:
        """Synthesize speech for a complete text message and write to a temporary WAV file."""
        model = self._get_model()
        audios = model.generate(
            text=text,
            instruct=instruct,
            speed=speed,
        )

        if not audios or len(audios) == 0:
            raise RuntimeError("OmniVoice produced empty audio output.")

        audio_data = audios[0]
        sampling_rate = getattr(model, "sampling_rate", 24000)

        import soundfile as sf

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            temp_wav_path = temp_wav.name

        sf.write(temp_wav_path, audio_data, sampling_rate)
        return temp_wav_path

    def speak(self, message: str) -> None:
        """
        Speak a message using OmniVoice neural voice synthesis.
        Synthesizes the complete message in a single continuous pass to maintain voice consistency.
        """
        if not message or not message.strip():
            return

        try:
            persona_name = self.config.get("persona", "agent_smith")
            voice_designs = self.config.get("voice_designs", {})
            persona_cfg = voice_designs.get(
                persona_name,
                {"instruct": "male, middle-aged, low pitch, american accent", "speed": 1.0},
            )

            instruct = persona_cfg.get("instruct", "male, middle-aged, low pitch, american accent")
            speed = persona_cfg.get("speed", 1.0)

            temp_wav_path = self._synthesize_to_file(message, instruct, speed)
            try:
                subprocess.run(["afplay", temp_wav_path], check=True)
            finally:
                if os.path.exists(temp_wav_path):
                    try:
                        os.remove(temp_wav_path)
                    except OSError:
                        pass

        except Exception as e:
            print(f"[mcp-speak] Error in OmniVoice synthesis: {e}", file=sys.stderr)
            if self.config.get("fallback_to_say", True):
                print("[mcp-speak] Falling back to macOS 'say' command...", file=sys.stderr)
                self._fallback_say.speak(message)
            else:
                raise


# Initialize configuration and active TTS engine
config = load_config()
if config.get("engine", "omnivoice").lower() == "omnivoice":
    engine = OmniVoiceEngine(config)
else:
    engine = SayEngine()

mcp = FastMCP("MacOS-Voice")

# Thread-safe queue for speech requests to guarantee strict sequential playback
speech_queue: queue.Queue = queue.Queue()


def speech_worker():
    """
    Dedicated worker thread that processes speech requests one by one.
    Guarantees no two speech outputs ever overlap.
    """
    while True:
        message, event = speech_queue.get()
        try:
            engine.speak(message)
        except Exception as e:
            print(f"[mcp-speak] Speech worker error: {e}", file=sys.stderr)
        finally:
            if event:
                event.set()
            speech_queue.task_done()


# Start background sequential worker thread
worker_thread = threading.Thread(target=speech_worker, daemon=True)
worker_thread.start()


@mcp.tool()
def speak(message: str) -> str:
    """
    Speaks the provided message aloud using neural Voice Design or macOS say.
    Blocking: waits until playback has completely finished before returning.
    """
    event = threading.Event()
    speech_queue.put((message, event))

    # Wait for sequential speech worker to finish speaking this message
    event.wait()
    return f"Finished speaking: {message}"


@mcp.tool()
def speak_non_blocking(message: str) -> str:
    """
    Speaks the provided message aloud using neural Voice Design or macOS say.
    Non-blocking: queues the message immediately and returns.
    Guarantees subsequent messages will be queued sequentially and not talk over each other.
    """
    # Number of items currently queued ahead (including any currently in progress)
    queue_pos = speech_queue.qsize() + 1
    speech_queue.put((message, None))
    return f"Queued for speaking (position {queue_pos}): {message}"


if __name__ == "__main__":
    mcp.run()
