from typing import Set

from .models import Story, ValidationResult
from .vocabulary import extract_words


def validate_story(
    story: Story,
    daily_focus_words: Set[str],
    learned_words: Set[str],
    min_words: int,
    max_words: int,
    min_daily_focus_words: int,
) -> ValidationResult:
    body_words = list(extract_words(story.body))
    used_daily_focus_words = daily_focus_words.intersection(body_words)
    # This list is informational only. Common words outside the textbook catalog
    # are expected and do not block publication.
    unknown = sorted({word for word in body_words if word not in learned_words})
    errors = []
    if len(body_words) < min_words:
        errors.append("Story is too short: {} words".format(len(body_words)))
    if len(body_words) > max_words:
        errors.append("Story is too long: {} words".format(len(body_words)))
    if not story.title.strip():
        errors.append("Story title is empty")
    if len(story.title.split()) > 10:
        errors.append("Story title is too long")
    if len(used_daily_focus_words) < min_daily_focus_words:
        errors.append(
            "Story uses only {} daily focus words; expected at least {}"
            .format(len(used_daily_focus_words), min_daily_focus_words)
        )
    return ValidationResult(
        ok=not errors,
        word_count=len(body_words),
        unknown_words=unknown,
        errors=errors,
    )
