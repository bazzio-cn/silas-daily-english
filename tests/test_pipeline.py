import json
import tempfile
import unittest
from pathlib import Path

from silas_daily_english.config import AppConfig
from silas_daily_english.pipeline import DailyPipeline
from silas_daily_english.storage import LocalPublisher
from silas_daily_english.story import MockStoryGenerator
from silas_daily_english.tts import MockTTS


class PipelineTest(unittest.TestCase):
    def test_local_publish_adds_episode_and_keeps_files_separate(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            pipeline = DailyPipeline(
                config=AppConfig.load(root / "data" / "config.json"),
                data_dir=root / "data",
                build_dir=temp / "build",
                publisher=LocalPublisher(temp / "site"),
                story_generator=MockStoryGenerator(),
                tts=MockTTS(),
            )
            episode = pipeline.publish("2026-06-01")
            self.assertEqual(episode.lesson, 39)
            self.assertTrue((temp / "site" / "episodes" / "2026-06-01.mp3").exists())
            self.assertTrue((temp / "site" / "episodes" / "2026-06-01.srt").exists())
            self.assertTrue((temp / "site" / "episodes" / "2026-06-01.txt").exists())
            state = json.loads((temp / "site" / "state.json").read_text())
            self.assertEqual(state["current_lesson"], 39)
            self.assertEqual(state["episodes"][0]["tts_voice"], "mock-voice")
            feed = (temp / "site" / "feed.xml").read_text()
            self.assertIn("episodes/2026-06-01.mp3", feed)
            self.assertIn("episodes/2026-06-01.srt", feed)
            self.assertIn("episodes/2026-06-01.txt", feed)
            self.assertNotIn("Daniel went to a small hospital", feed)
            transcript = (temp / "site" / "episodes" / "2026-06-01.txt").read_text()
            self.assertIn("successful", transcript)
            self.assertIn("following", transcript)

    def test_duplicate_date_is_rejected(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            pipeline = DailyPipeline(
                config=AppConfig.load(root / "data" / "config.json"),
                data_dir=root / "data",
                build_dir=temp / "build",
                publisher=LocalPublisher(temp / "site"),
                story_generator=MockStoryGenerator(),
                tts=MockTTS(),
            )
            pipeline.publish("2026-06-01")
            with self.assertRaisesRegex(RuntimeError, "already exists"):
                pipeline.publish("2026-06-01")

    def test_missing_next_lesson_stops_publish(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            publisher = LocalPublisher(temp / "site")
            (temp / "site").mkdir()
            (temp / "site" / "state.json").write_text(
                '{"current_lesson": 96, "last_published_date": "2026-07-28", '
                '"status": "active", "episodes": []}'
            )
            pipeline = DailyPipeline(
                config=AppConfig.load(root / "data" / "config.json"),
                data_dir=root / "data",
                build_dir=temp / "build",
                publisher=publisher,
                story_generator=MockStoryGenerator(),
                tts=MockTTS(),
            )
            with self.assertRaisesRegex(RuntimeError, "complete through lesson 96"):
                pipeline.publish("2026-07-29")


if __name__ == "__main__":
    unittest.main()
