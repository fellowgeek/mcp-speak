import os
import sys
from pathlib import Path

# Auto-re-execute using .venv python if available and not already inside a virtualenv
PROJECT_DIR = Path(__file__).parent.parent.resolve()
VENV_PYTHON = PROJECT_DIR / ".venv" / "bin" / "python"
if sys.prefix == sys.base_prefix and VENV_PYTHON.exists():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import unittest
import time
import json
import tempfile
import threading
from unittest.mock import patch, MagicMock

import speak_server
from speak_server import (
    load_config,
    SayEngine,
    OmniVoiceEngine,
    speak,
    speak_non_blocking,
    speech_queue,
)


class TestSpeakServer(unittest.TestCase):

    def test_load_config_defaults(self):
        config = load_config()
        self.assertIn("engine", config)
        self.assertIn("persona", config)
        self.assertIn("voice_designs", config)
        self.assertIn("agent_smith", config["voice_designs"])
        self.assertIn("instruct", config["voice_designs"]["agent_smith"])
        self.assertIn("neutral_mainframe", config["voice_designs"])
        self.assertIn("nature_narrator", config["voice_designs"])
        self.assertIn("head_chef", config["voice_designs"])

    def test_load_config_env_overrides(self):
        with patch.dict(
            "os.environ",
            {
                "MCP_SPEAK_ENGINE": "say",
                "MCP_SPEAK_PERSONA": "neutral_mainframe",
                "MCP_SPEAK_DEVICE": "cpu",
            },
        ):
            config = load_config()
            self.assertEqual(config["engine"], "say")
            self.assertEqual(config["persona"], "neutral_mainframe")
            self.assertEqual(config["device"], "cpu")

    @patch("subprocess.run")
    def test_say_engine(self, mock_run):
        engine = SayEngine()
        engine.speak("Hello world")
        mock_run.assert_called_once_with(["say", "Hello world"], check=True)

    @patch("subprocess.run")
    def test_omnivoice_single_pass_synthesis_and_cleanup(self, mock_run):
        """
        Verify that OmniVoice synthesizes the complete message in a single pass
        and cleans up temporary WAV audio files after playback.
        """
        config = {
            "engine": "omnivoice",
            "persona": "neutral_mainframe",
            "fallback_to_say": False,
            "voice_designs": {
                "neutral_mainframe": {"instruct": "neutral, monotone", "speed": 1.0}
            },
        }
        engine = OmniVoiceEngine(config)

        created_temp_files = []

        def mock_synthesize(text, instruct, speed):
            fd, path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            created_temp_files.append(path)
            return path

        engine._synthesize_to_file = MagicMock(side_effect=mock_synthesize)

        message = "This is sentence one. This is sentence two. Everything is synthesized as one continuous audio pass."
        engine.speak(message)

        # Verify synthesize was called once with the complete message
        engine._synthesize_to_file.assert_called_once_with(
            message, "neutral, monotone", 1.0
        )

        # Verify afplay was invoked with the temporary file
        mock_run.assert_called_once_with(["afplay", created_temp_files[0]], check=True)

        # Verify the temporary audio file was deleted
        self.assertFalse(os.path.exists(created_temp_files[0]))

    @patch("subprocess.run")
    def test_omnivoice_fallback_to_say(self, mock_run):
        """Configure OmniVoice engine with broken model to trigger fallback to macOS say."""
        config = {
            "engine": "omnivoice",
            "persona": "agent_smith",
            "fallback_to_say": True,
            "voice_designs": {
                "agent_smith": {"instruct": "male, low pitch", "speed": 1.0}
            },
        }
        engine = OmniVoiceEngine(config)
        engine._get_model = MagicMock(side_effect=RuntimeError("Model load failed"))
        engine.speak("Fallback test message. Complete sentence.")
        mock_run.assert_called_once_with(
            ["say", "Fallback test message. Complete sentence."], check=True
        )

    @patch("subprocess.run")
    def test_sequential_queue_prevents_overlap(self, mock_run):
        """Test that multiple speak_non_blocking requests are queued sequentially and executed one by one."""
        execution_order = []

        def slow_playback(cmd, check=True):
            execution_order.append(f"start:{cmd[1]}")
            time.sleep(0.05)
            execution_order.append(f"end:{cmd[1]}")

        mock_run.side_effect = slow_playback

        speak_server.engine = SayEngine()

        res1 = speak_non_blocking("Message 1")
        res2 = speak_non_blocking("Message 2")
        res3 = speak_non_blocking("Message 3")

        self.assertIn("Queued for speaking", res1)
        self.assertIn("Queued for speaking", res2)
        self.assertIn("Queued for speaking", res3)

        speech_queue.join()

        self.assertEqual(
            execution_order,
            [
                "start:Message 1",
                "end:Message 1",
                "start:Message 2",
                "end:Message 2",
                "start:Message 3",
                "end:Message 3",
            ],
        )


if __name__ == "__main__":
    unittest.main()
