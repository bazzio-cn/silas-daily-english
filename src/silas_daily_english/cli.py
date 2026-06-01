import argparse
import os
import random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import AppConfig
from .pipeline import DailyPipeline
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
    tts = MockTTS() if args.tts_provider == "mock" else AzureTTS(selected_voice)
    pipeline = DailyPipeline(
        config=config,
        data_dir=data_dir,
        build_dir=root / "build" / "latest",
        publisher=publisher,
        story_generator=story_generator,
        tts=tts,
    )
    episode = pipeline.publish(args.date, lesson=args.lesson)
    print(
        "Published {} for lesson {}: {}".format(
            episode.date, episode.lesson, episode.title
        )
    )


if __name__ == "__main__":
    main()
