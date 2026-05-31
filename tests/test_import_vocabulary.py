import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "import_vocabulary.py"
SPEC = importlib.util.spec_from_file_location("import_vocabulary", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ImportVocabularyTest(unittest.TestCase):
    def test_parse_words_extracts_cards_without_duplicates(self):
        html = """
        <div class="word-card"><div class="word-text">operation</div></div>
        <div class="word-card"><div class="word-text">successful</div></div>
        <div class="word-card"><div class="word-text">operation</div></div>
        """
        self.assertEqual(MODULE.parse_words(html), ["operation", "successful"])


if __name__ == "__main__":
    unittest.main()
