import unittest
from types import SimpleNamespace

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

    def test_cancellation_message_uses_python_result_details(self):
        tts = object.__new__(AzureTTS)
        tts.voice = "en-GB-RyanNeural"
        result = SimpleNamespace(
            cancellation_details=SimpleNamespace(
                reason="Error",
                error_code="AuthenticationFailure",
                error_details="Invalid subscription key",
            )
        )

        message = tts._cancellation_message(result)

        self.assertIn("en-GB-RyanNeural", message)
        self.assertIn("AuthenticationFailure", message)
        self.assertIn("Invalid subscription key", message)


if __name__ == "__main__":
    unittest.main()
