import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from silas_daily_english import cli


class CliTest(unittest.TestCase):
    def test_cli_reads_data_from_working_directory(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            local_root = Path(temp_dir) / "site"
            argv = [
                "silas-daily-english",
                "publish",
                "--date",
                "2026-06-01",
                "--publisher",
                "local",
                "--story-provider",
                "mock",
                "--tts-provider",
                "mock",
                "--local-root",
                str(local_root),
            ]
            with patch("sys.argv", argv), patch("pathlib.Path.cwd", return_value=root):
                cli.main()
            self.assertTrue((local_root / "feed.xml").exists())


if __name__ == "__main__":
    unittest.main()
