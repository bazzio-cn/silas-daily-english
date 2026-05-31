import unittest

from silas_daily_english.subtitles import estimated_boundaries, format_srt


class SubtitleTest(unittest.TestCase):
    def test_srt_contains_timestamps_and_text(self):
        result = format_srt(estimated_boundaries("Hello Aron. Welcome home.", 4))
        self.assertIn("00:00:00,000 -->", result)
        self.assertIn("Hello Aron.", result)
        self.assertIn("Welcome home.", result)


if __name__ == "__main__":
    unittest.main()
