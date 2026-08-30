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
            text=message, instruct="neutral, monotone", speed=1.0
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

    @patch("subprocess.run")
    def test_voice_clone_mode_when_wav_present(self, mock_run):
        """Verify that OmniVoice uses voice cloning when reference WAV and optional transcript TXT exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            wav_file = temp_dir_path / "pun_master.wav"
            txt_file = temp_dir_path / "pun_master.txt"
            wav_file.write_bytes(b"dummy_wav_data")
            txt_file.write_text("This is a sample reference transcript.", encoding="utf-8")

            config = {
                "engine": "omnivoice",
                "persona": "pun_master",
                "voices_dir": str(temp_dir_path),
                "fallback_to_say": False,
                "voice_designs": {
                    "pun_master": {"instruct": "male, witty", "speed": 1.05}
                },
            }
            engine = OmniVoiceEngine(config)

            # Mock model
            mock_model = MagicMock()
            mock_prompt = MagicMock()
            mock_model.create_voice_clone_prompt.return_value = mock_prompt
            mock_model.generate.return_value = [[0.0] * 24000]
            mock_model.sampling_rate = 24000
            engine._get_model = MagicMock(return_value=mock_model)

            with patch("soundfile.write"):
                engine.speak("Testing cloned speech synthesis.")

            # Verify create_voice_clone_prompt was called with the wav path and transcript text
            mock_model.create_voice_clone_prompt.assert_called_once_with(
                ref_audio=str(wav_file),
                ref_text="This is a sample reference transcript.",
            )

            # Verify generate was called with voice_clone_prompt
            mock_model.generate.assert_called_once_with(
                text="Testing cloned speech synthesis.",
                voice_clone_prompt=mock_prompt,
                speed=1.05,
            )

    @patch("subprocess.run")
    def test_voice_clone_prompt_caching(self, mock_run):
        """Verify that VoiceClonePrompt is cached in memory across multiple speak calls."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            wav_file = temp_dir_path / "nature_narrator.wav"
            wav_file.write_bytes(b"dummy_wav_data")

            config = {
                "engine": "omnivoice",
                "persona": "nature_narrator",
                "voices_dir": str(temp_dir_path),
                "fallback_to_say": False,
                "voice_designs": {
                    "nature_narrator": {"instruct": "male, narrator", "speed": 0.95}
                },
            }
            engine = OmniVoiceEngine(config)

            mock_model = MagicMock()
            mock_prompt = MagicMock()
            mock_model.create_voice_clone_prompt.return_value = mock_prompt
            mock_model.generate.return_value = [[0.0] * 24000]
            mock_model.sampling_rate = 24000
            engine._get_model = MagicMock(return_value=mock_model)

            with patch("soundfile.write"):
                engine.speak("Sentence one.")
                engine.speak("Sentence two.")

            # create_voice_clone_prompt should only be called once because of prompt caching
            self.assertEqual(mock_model.create_voice_clone_prompt.call_count, 1)
            self.assertEqual(mock_model.generate.call_count, 2)

    @patch("subprocess.run")
    def test_fallback_to_voice_design_when_wav_absent(self, mock_run):
        """Verify that OmniVoice falls back to instruction-based Voice Design when no WAV file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Empty voices dir
            config = {
                "engine": "omnivoice",
                "persona": "sarcastic_senior",
                "voices_dir": str(temp_dir),
                "fallback_to_say": False,
                "voice_designs": {
                    "sarcastic_senior": {"instruct": "male, sarcastic, low pitch", "speed": 1.0}
                },
            }
            engine = OmniVoiceEngine(config)

            mock_model = MagicMock()
            mock_model.generate.return_value = [[0.0] * 24000]
            mock_model.sampling_rate = 24000
            engine._get_model = MagicMock(return_value=mock_model)

            with patch("soundfile.write"):
                engine.speak("Hello there.")

            # Voice clone prompt should not be created
            mock_model.create_voice_clone_prompt.assert_not_called()

            # Voice design instruct should be used
            mock_model.generate.assert_called_once_with(
                text="Hello there.",
                instruct="male, sarcastic, low pitch",
                speed=1.0,
            )


if __name__ == "__main__":
    unittest.main()
