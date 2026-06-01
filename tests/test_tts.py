import unittest

from silas_daily_english.tts import AzureTTS


class AzureTTSTest(unittest.TestCase):
    def test_ssml_applies_rate_and_escapes_text(self):
        tts = object.__new__(AzureTTS)
        tts.voice = "en-GB-RyanNeural"
        tts.rate_percent = -10
        ssml = tts._ssml("Tea & toast < breakfast")
        self.assertIn('rate="-10%"', ssml)
        self.assertIn('name="en-GB-RyanNeural"', ssml)
        self.assertIn("Tea &amp; toast &lt; breakfast", ssml)


if __name__ == "__main__":
    unittest.main()
