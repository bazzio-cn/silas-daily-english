import unittest
from pathlib import Path

from silas_daily_english.vocabulary import VocabularyCatalog


class VocabularyCatalogTest(unittest.TestCase):
    def test_lessons_after_catalog_end_use_final_lesson(self):
        root = Path(__file__).resolve().parents[1]
        vocabulary = VocabularyCatalog(root / "data")
        self.assertEqual(vocabulary.resolve_lesson(97), 96)
        self.assertEqual(vocabulary.lesson_words(97), vocabulary.lesson_words(96))
        self.assertIn("spectacle", vocabulary.learned_words(97))


if __name__ == "__main__":
    unittest.main()
