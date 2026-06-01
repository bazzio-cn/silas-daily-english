import unittest
from pathlib import Path

from silas_daily_english.config import AppConfig


class ConfigTest(unittest.TestCase):
    def test_voice_pool_has_four_british_and_four_american_voices(self):
        root = Path(__file__).resolve().parents[1]
        config = AppConfig.load(root / "data" / "config.json")
        self.assertEqual(len(config.tts_voices), 8)
        self.assertEqual(
            len([voice for voice in config.tts_voices if voice.startswith("en-GB-")]),
            4,
        )
        self.assertEqual(
            len([voice for voice in config.tts_voices if voice.startswith("en-US-")]),
            4,
        )
        self.assertEqual(len(set(config.tts_voices)), 8)

    def test_story_config_has_recurring_characters_and_weighted_themes(self):
        root = Path(__file__).resolve().parents[1]
        config = AppConfig.load(root / "data" / "config.json")
        self.assertEqual(len(config.recurring_characters), 4)
        self.assertEqual(len(config.story_themes), 5)
        self.assertEqual(sum(theme["weight"] for theme in config.story_themes), 100)


if __name__ == "__main__":
    unittest.main()
