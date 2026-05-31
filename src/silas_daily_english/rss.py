from datetime import datetime
from email.utils import format_datetime
from html import escape
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

from .config import AppConfig
from .models import Episode


def write_feed(config: AppConfig, episodes: Iterable[Episode], path: Path) -> None:
    base_url = config.public_base_url.rstrip("/")
    items = "\n".join(_render_item(base_url, episode) for episode in episodes)
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:podcast="https://podcastindex.org/namespace/1.0">
  <channel>
    <title>{title}</title>
    <link>{base_url}/feed.xml</link>
    <atom:link href="{base_url}/feed.xml" rel="self" type="application/rss+xml" />
    <language>en-gb</language>
    <description>{description}</description>
    <itunes:author>{author}</itunes:author>
    <itunes:image href="{base_url}/cover.png" />
    <itunes:explicit>false</itunes:explicit>
    <itunes:block>yes</itunes:block>
{items}
  </channel>
</rss>
""".format(
        title=escape(config.podcast_title),
        description=escape(config.podcast_description),
        author=escape(config.podcast_author),
        base_url=escape(base_url, quote=True),
        items=items,
    )
    path.write_text(xml, encoding="utf-8")


def _render_item(base_url: str, episode: Episode) -> str:
    episode_url = "{}/episodes/{}".format(base_url, episode.date)
    publication = datetime.fromisoformat(episode.date).replace(
        hour=6, minute=17, tzinfo=ZoneInfo("Asia/Bangkok")
    )
    return """    <item>
      <title>{title}</title>
      <description><![CDATA[
        <p>{description}</p>
        <p><a href="{episode_url}.txt">Read the transcript</a></p>
      ]]></description>
      <pubDate>{publication}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
      <enclosure url="{episode_url}.mp3" length="{audio_bytes}" type="audio/mpeg" />
      <itunes:duration>{duration}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
      <podcast:transcript url="{episode_url}.srt" type="application/srt" language="en-gb" />
    </item>""".format(
        title=escape(episode.title),
        description=escape(episode.description),
        publication=format_datetime(publication),
        guid=escape(episode.guid),
        episode_url=escape(episode_url, quote=True),
        audio_bytes=episode.audio_bytes,
        duration=_duration(episode.duration_seconds),
    )


def _duration(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    return "{:02d}:{:02d}".format(minutes, seconds)
