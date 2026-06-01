import random
from typing import Dict, Iterable, List


def select_theme(themes: List[Dict], recent_themes: Iterable[str]) -> Dict:
    recent = [theme for theme in recent_themes if theme]
    available = [theme for theme in themes if theme["key"] not in recent]
    if not available:
        most_recent = recent[0] if recent else ""
        available = [theme for theme in themes if theme["key"] != most_recent]
    if not available:
        available = themes
    return random.SystemRandom().choices(
        available,
        weights=[theme["weight"] for theme in available],
        k=1,
    )[0]
