#!/usr/bin/env python3
"""Import New Concept English 2 lesson vocabulary from lesson pages."""

import argparse
import json
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import List
from urllib.request import Request, urlopen


class LessonVocabularyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.words: List[str] = []
        self._inside_word_text = False

    def handle_starttag(self, tag: str, attrs) -> None:
        classes = dict(attrs).get("class", "").split()
        if tag == "div" and "word-text" in classes:
            self._inside_word_text = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self._inside_word_text:
            self._inside_word_text = False

    def handle_data(self, data: str) -> None:
        if self._inside_word_text:
            word = data.strip()
            if word and word not in self.words:
                self.words.append(word)


def parse_words(html: str) -> List[str]:
    parser = LessonVocabularyParser()
    parser.feed(html)
    return parser.words


def fetch_lesson(base_url: str, lesson: int) -> str:
    url = "{}?id=2-{:03d}".format(base_url.rstrip("?"), lesson)
    request = Request(url, headers={"User-Agent": "silas-daily-english/0.1"})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=96)
    parser.add_argument(
        "--base-url",
        default="https://newconceptenglish.com/index.php",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "lessons.json",
    )
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()

    lessons = {}
    for lesson in range(args.start, args.end + 1):
        words = parse_words(fetch_lesson(args.base_url, lesson))
        if not words:
            raise RuntimeError("No vocabulary found for lesson {}".format(lesson))
        lessons[str(lesson)] = words
        print("Lesson {:03d}: {} words".format(lesson, len(words)))
        time.sleep(args.delay)

    payload = {
        "catalog_complete_through": args.end,
        "lessons": lessons,
    }
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Wrote {}".format(args.output))


if __name__ == "__main__":
    main()
