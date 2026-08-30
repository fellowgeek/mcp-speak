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
    "voices_dir": "voices",
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
    if "MCP_SPEAK_VOICES_DIR" in os.environ:
        config["voices_dir"] = os.environ["MCP_SPEAK_VOICES_DIR"].strip()

    return config


class SayEngine:
    """Fallback TTS engine using native macOS 'say' command."""

    def speak(self, message: str) -> None:
        subprocess.run(["say", message], check=True)


class OmniVoiceEngine:
    """Neural TTS engine using OmniVoice with zero-shot Voice Design, Voice Cloning, and pipelined streaming."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.device = None
        self._lock = threading.Lock()
        self._fallback_say = SayEngine()
        self._voice_clone_prompts: Dict[str, Any] = {}

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

    def _get_voices_dir(self) -> Path:
        """Resolve the path to the voices directory."""
        configured_dir = Path(self.config.get("voices_dir", "voices"))
        if configured_dir.is_absolute():
            return configured_dir
        return SCRIPT_DIR / configured_dir

    def _resolve_voice_clone_prompt(self, persona_name: str) -> Optional[Any]:
        """
        Check if a reference voice file exists for the persona and load/generate its VoiceClonePrompt.
        Caches the prompt in memory for subsequent speech calls.
        """
        if persona_name in self._voice_clone_prompts:
            return self._voice_clone_prompts[persona_name]

        voices_dir = self._get_voices_dir()
        if not voices_dir.exists():
            return None

        pt_file = voices_dir / f"{persona_name}.pt"
        wav_file = voices_dir / f"{persona_name}.wav"

        # Check for pre-saved VoiceClonePrompt .pt file
        if pt_file.exists():
            try:
                from omnivoice.models.omnivoice import VoiceClonePrompt

                prompt = VoiceClonePrompt.load(str(pt_file))
                self._voice_clone_prompts[persona_name] = prompt
                print(
                    f"[mcp-speak] Loaded pre-cached voice clone prompt for persona '{persona_name}' from {pt_file.name}",
                    file=sys.stderr,
                )
                return prompt
            except Exception as e:
                print(
                    f"[mcp-speak] Warning: Failed to load cached prompt {pt_file.name}: {e}",
                    file=sys.stderr,
                )

        # Check for reference WAV file
        if wav_file.exists():
            try:
                txt_file = voices_dir / f"{persona_name}.txt"
                ref_text = None
                if txt_file.exists():
                    try:
                        ref_text = txt_file.read_text(encoding="utf-8").strip()
                    except Exception as e:
                        print(
                            f"[mcp-speak] Warning: Failed to read transcript {txt_file.name}: {e}",
                            file=sys.stderr,
                        )

                model = self._get_model()
                print(
                    f"[mcp-speak] Creating voice clone prompt from '{wav_file.name}' for persona '{persona_name}' "
                    f"(transcript provided: {ref_text is not None})...",
                    file=sys.stderr,
                )
                prompt = model.create_voice_clone_prompt(
                    ref_audio=str(wav_file),
                    ref_text=ref_text,
                )
                self._voice_clone_prompts[persona_name] = prompt
                return prompt
            except Exception as e:
                print(
                    f"[mcp-speak] Warning: Failed to create voice clone prompt from {wav_file.name}: {e}",
                    file=sys.stderr,
                )
                return None

        return None

    def _synthesize_to_file(
        self,
        text: str,
        instruct: Optional[str] = None,
        speed: float = 1.0,
        voice_clone_prompt: Optional[Any] = None,
    ) -> str:
        """Synthesize speech for a complete text message and write to a temporary WAV file."""
        model = self._get_model()
        if voice_clone_prompt is not None:
            audios = model.generate(
                text=text,
                voice_clone_prompt=voice_clone_prompt,
                speed=speed,
            )
        else:
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
        Prefers cloned voice if reference audio exists, otherwise falls back to Voice Design.
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
            speed = persona_cfg.get("speed", 1.0)

            # Check if reference audio exists for persona voice cloning
            voice_clone_prompt = self._resolve_voice_clone_prompt(persona_name)

            if voice_clone_prompt is not None:
                temp_wav_path = self._synthesize_to_file(
                    text=message,
                    speed=speed,
                    voice_clone_prompt=voice_clone_prompt,
                )
            else:
                instruct = persona_cfg.get("instruct", "male, middle-aged, low pitch, american accent")
                temp_wav_path = self._synthesize_to_file(
                    text=message,
                    instruct=instruct,
                    speed=speed,
                )

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
