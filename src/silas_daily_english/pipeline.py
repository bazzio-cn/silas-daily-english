import json
from datetime import date
from pathlib import Path
from typing import Optional

from .config import AppConfig, load_json
from .models import Episode, State
from .rss import write_feed
from .themes import select_theme
from .validate import validate_story
from .vocabulary import VocabularyCatalog


class DailyPipeline:
    def __init__(
        self,
        config: AppConfig,
        data_dir: Path,
        build_dir: Path,
        publisher,
        story_generator,
        tts,
        theme_selector=select_theme,
    ):
        self.config = config
        self.data_dir = data_dir
        self.build_dir = build_dir
        self.publisher = publisher
        self.story_generator = story_generator
        self.tts = tts
        self.theme_selector = theme_selector
        self.vocabulary = VocabularyCatalog(data_dir)

    def publish(self, publication_date: str, lesson: Optional[int] = None) -> Episode:
        self.build_dir.mkdir(parents=True, exist_ok=True)
        state = self._load_state()
        if any(item.date == publication_date for item in state.episodes):
            raise RuntimeError("Episode already exists for {}".format(publication_date))
        target_lesson = lesson or state.current_lesson + 1
        self.vocabulary.ensure_available(target_lesson)
        theme = self.theme_selector(
            self.config.story_themes,
            [episode.story_theme for episode in state.episodes[:14]],
        )
        story = self._generate_story(target_lesson, theme)

        stem = publication_date
        audio_path = self.build_dir / "{}.mp3".format(stem)
        subtitle_path = self.build_dir / "{}.srt".format(stem)
        text_path = self.build_dir / "{}.txt".format(stem)
        text_path.write_text("{}\n\n{}\n".format(story.title, story.body), encoding="utf-8")
        duration_seconds = self.tts.synthesize(
            "{}\n\n{}".format(story.title, story.body),
            audio_path,
            subtitle_path,
        )
        episode = Episode(
            date=publication_date,
            lesson=target_lesson,
            title=story.title,
            description="An original short English story.",
            duration_seconds=duration_seconds,
            audio_bytes=audio_path.stat().st_size,
            guid="silas-daily-english-{}".format(publication_date),
            tts_voice=self.tts.voice,
            story_theme=theme["key"],
        )
        state.current_lesson = target_lesson
        state.last_published_date = publication_date
        state.episodes.insert(0, episode)
        state.episodes = state.episodes[: self.config.feed_item_limit]

        feed_path = self.build_dir / "feed.xml"
        state_path = self.build_dir / "state.json"
        write_feed(self.config, state.episodes, feed_path)
        state_path.write_text(
            json.dumps(state.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        # Publish the immutable episode files before exposing the RSS item.
        self.publisher.upload(text_path, "episodes/{}.txt".format(stem))
        self.publisher.upload(subtitle_path, "episodes/{}.srt".format(stem))
        self.publisher.upload(audio_path, "episodes/{}.mp3".format(stem))
        self.publisher.upload(feed_path, "feed.xml")
        self.publisher.upload(state_path, "state.json")
        return episode

    def _load_state(self) -> State:
        payload = self.publisher.load_state()
        if payload is None:
            payload = load_json(self.data_dir / "state.default.json")
        return State.from_dict(payload)

    def _generate_story(self, lesson: int, theme: dict):
        daily_focus_words = self.vocabulary.lesson_words(lesson)
        learned_words = self.vocabulary.learned_words(lesson)
        last_errors = []
        for attempt in range(1, self.config.max_generation_attempts + 1):
            story = self.story_generator.generate(
                lesson,
                daily_focus_words,
                learned_words,
                theme,
                self.config.recurring_characters,
                self.config.story_min_words,
                self.config.story_max_words,
                attempt,
            )
            validation = validate_story(
                story,
                set(word.lower() for word in daily_focus_words),
                learned_words,
                self.config.story_min_words,
                self.config.story_max_words,
                self.config.min_daily_focus_words,
            )
            if validation.ok:
                return story
            last_errors = validation.errors
        raise RuntimeError("Story validation failed: {}".format("; ".join(last_errors)))
