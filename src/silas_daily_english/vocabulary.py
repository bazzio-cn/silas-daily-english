import re
from pathlib import Path
from typing import Dict, Iterable, List, Set

from .config import load_json


WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


class VocabularyCatalog:
    def __init__(self, data_dir: Path):
        payload = load_json(data_dir / "lessons.json")
        self.catalog_complete_through = int(payload["catalog_complete_through"])
        self.lessons: Dict[int, List[str]] = {
            int(number): words for number, words in payload["lessons"].items()
        }
        self.base_words = {
            line.strip().lower()
            for line in (data_dir / "base_words.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }

    def ensure_available(self, lesson: int) -> None:
        if lesson > self.catalog_complete_through:
            raise RuntimeError(
                "Vocabulary catalog is complete through lesson {}, but lesson {} was requested."
                .format(self.catalog_complete_through, lesson)
            )

    def learned_words(self, lesson: int) -> Set[str]:
        self.ensure_available(lesson)
        words = set(self.base_words)
        for number, lesson_words in self.lessons.items():
            if number <= lesson:
                words.update(word.lower() for word in lesson_words)
        return words

    def lesson_words(self, lesson: int) -> List[str]:
        self.ensure_available(lesson)
        return self.lessons.get(lesson, [])


def extract_words(text: str) -> Iterable[str]:
    return (match.group(0).lower() for match in WORD_RE.finditer(text))
