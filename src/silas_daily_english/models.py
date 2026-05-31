from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class Episode:
    date: str
    lesson: int
    title: str
    description: str
    duration_seconds: int
    audio_bytes: int
    guid: str

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "Episode":
        return cls(**value)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class State:
    current_lesson: int
    last_published_date: str
    status: str = "active"
    episodes: List[Episode] = field(default_factory=list)

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "State":
        episodes = [Episode.from_dict(item) for item in value.get("episodes", [])]
        return cls(
            current_lesson=value["current_lesson"],
            last_published_date=value["last_published_date"],
            status=value.get("status", "active"),
            episodes=episodes,
        )

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["episodes"] = [episode.to_dict() for episode in self.episodes]
        return result


@dataclass
class Story:
    title: str
    body: str


@dataclass
class ValidationResult:
    ok: bool
    word_count: int
    unknown_words: List[str]
    errors: List[str]
