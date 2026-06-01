import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class AppConfig:
    podcast_title: str
    podcast_description: str
    podcast_author: str
    public_base_url: str
    cos_prefix: str
    feed_item_limit: int
    story_min_words: int
    story_max_words: int
    min_daily_focus_words: int
    max_generation_attempts: int
    tts_voices: List[str]

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        return cls(**json.loads(path.read_text(encoding="utf-8")))


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError("Missing required environment variable: {}".format(name))
    return value
