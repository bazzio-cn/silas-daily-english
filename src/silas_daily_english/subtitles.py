import re
from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Boundary:
    text: str
    start_seconds: float
    duration_seconds: float


def format_srt(boundaries: Iterable[Boundary], max_chars: int = 68) -> str:
    cues: List[List[Boundary]] = []
    current: List[Boundary] = []
    current_length = 0
    for boundary in boundaries:
        separator = 1 if current else 0
        if current and current_length + separator + len(boundary.text) > max_chars:
            cues.append(current)
            current = []
            current_length = 0
        current.append(boundary)
        current_length += separator + len(boundary.text)
        if re.search(r"[.!?]$", boundary.text):
            cues.append(current)
            current = []
            current_length = 0
    if current:
        cues.append(current)

    lines = []
    for index, cue in enumerate(cues, start=1):
        start = cue[0].start_seconds
        end = cue[-1].start_seconds + max(cue[-1].duration_seconds, 0.25)
        lines.extend(
            [
                str(index),
                "{} --> {}".format(_timestamp(start), _timestamp(end)),
                " ".join(item.text for item in cue),
                "",
            ]
        )
    return "\n".join(lines)


def estimated_boundaries(text: str, duration_seconds: float) -> List[Boundary]:
    words = re.findall(r"\S+", text)
    if not words:
        return []
    step = duration_seconds / len(words)
    return [
        Boundary(text=word, start_seconds=index * step, duration_seconds=step)
        for index, word in enumerate(words)
    ]


def _timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1_000)
    return "{:02d}:{:02d}:{:02d},{:03d}".format(
        hours, minutes, seconds, milliseconds
    )
