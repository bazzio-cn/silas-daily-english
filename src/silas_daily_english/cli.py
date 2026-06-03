import argparse
import os
import random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import AppConfig
from .emailer import NullEmailSender, SMTPEmailSender
from .pipeline import DailyPipeline
from .questions import MockQuestionGenerator, OpenAIQuestionGenerator
from .storage import COSPublisher, LocalPublisher
from .story import MockStoryGenerator, OpenAIStoryGenerator
from .tts import AzureTTS, MockTTS


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish Silas' Daily English")
    parser.add_argument("command", choices=["publish"])
    parser.add_argument(
        "--date",
        default=datetime.now(ZoneInfo("Asia/Bangkok")).date().isoformat(),
    )
    parser.add_argument("--lesson", type=int)
    parser.add_argument("--publisher", choices=["local", "cos"], default="local")
    parser.add_argument("--story-provider", choices=["mock", "openai"], default="mock")
    parser.add_argument("--tts-provider", choices=["mock", "azure"], default="mock")
    parser.add_argument(
        "--question-provider",
        choices=["none", "mock", "openai"],
        default="none",
    )
    parser.add_argument("--question-email", choices=["none", "smtp"], default="none")
    parser.add_argument("--local-root", default="build/site")
    args = parser.parse_args()

    root = Path(os.environ.get("SILAS_DAILY_ENGLISH_ROOT", Path.cwd())).resolve()
    data_dir = root / "data"
    config = AppConfig.load(data_dir / "config.json")
    publisher = LocalPublisher(Path(args.local_root)) if args.publisher == "local" else COSPublisher()
    story_generator = (
        MockStoryGenerator()
        if args.story_provider == "mock"
        else OpenAIStoryGenerator()
    )
    selected_voice = random.SystemRandom().choice(config.tts_voices)
    tts = (
        MockTTS()
        if args.tts_provider == "mock"
        else AzureTTS(selected_voice, config.tts_rate_percent)
    )
    question_generator = None
    if args.question_provider == "mock":
        question_generator = MockQuestionGenerator()
    elif args.question_provider == "openai":
        question_generator = OpenAIQuestionGenerator()
    email_sender = None
    if args.question_email == "none":
        email_sender = NullEmailSender()
    elif args.question_email == "smtp":
        email_sender = SMTPEmailSender.from_env()
    pipeline = DailyPipeline(
        config=config,
        data_dir=data_dir,
        build_dir=root / "build" / "latest",
        publisher=publisher,
        story_generator=story_generator,
        tts=tts,
        question_generator=question_generator,
        email_sender=email_sender,
    )
    episode = pipeline.publish(args.date, lesson=args.lesson)
    print(
        "Published {} for lesson {}: {}".format(
            episode.date, episode.lesson, episode.title
        )
    )


if __name__ == "__main__":
    main()
