# Silas' Daily English

Automated private podcast publishing for Aron's daily English listening practice.

Each run creates one original short story, an English MP3, a timed SRT
transcript, a plain-text transcript, and an updated RSS feed. Episode assets stay
separate from `feed.xml`.

Each episode randomly selects one of eight clear neural voices: four British
English voices and four American English voices, with two male and two female
voices in each accent. The selected voice is recorded in `state.json`.

Stories use an original light school-life series with recurring characters:
Leo, Mia, Ben, and Ms Green. Each run chooses a weighted theme such as school
comedy, family life, a small adventure, science curiosity, or travel discovery.
The publisher avoids recently used themes when possible and records the selected
theme in `state.json`.

Stories target 200-260 words. Azure Speech reads each episode at a 10% slower
rate to keep the daily listening task comfortable.

## Current Status

The publishing pipeline, local dry-run provider, Azure Speech provider, OpenAI
story provider, COS publisher, RSS builder, tests, and GitHub Actions workflow
are implemented.

`data/lessons.json` contains the imported New Concept English 2 vocabulary catalog
for Lessons 1-96. Each entry records the new vocabulary introduced by that lesson.
Common primary-school English is allowed from the start; the textbook vocabulary
is a daily focus list, not a strict whitelist. The program stops after Lesson 96
until a new learning plan is configured.

Refresh the vocabulary catalog from the lesson pages:

```bash
python3 scripts/import_vocabulary.py --start 1 --end 96
```

## Local Dry Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
silas-daily-english publish \
  --date 2026-06-01 \
  --publisher local \
  --story-provider mock \
  --tts-provider mock
```

Generated files appear in `build/site/`.

## Production Secrets

Add these GitHub Actions repository secrets:

```text
OPENAI_API_KEY
AZURE_SPEECH_KEY
AZURE_SPEECH_REGION
TENCENT_SECRET_ID
TENCENT_SECRET_KEY
```

Add these repository variables:

```text
COS_BUCKET=silas-podcast-1252641701
COS_REGION=ap-guangzhou
COS_PREFIX=aron-8f3a91
```

Use a Tencent Cloud CAM sub-account restricted to this COS bucket. Do not store
the Tencent Cloud primary account key in GitHub.

## Publication Order

The publisher uploads files in this order:

```text
episodes/YYYY-MM-DD.txt
episodes/YYYY-MM-DD.srt
episodes/YYYY-MM-DD.mp3
feed.xml
state.json
```

The RSS feed is updated only after the episode files are available.

Re-running the workflow for an existing date regenerates that day's story,
audio, and transcripts from scratch, then replaces the RSS item. It keeps the
original lesson number so the learning progress is not advanced twice. A
different explicit lesson override for an existing date is rejected.

## Private Apple Podcasts Limitation

Apple Podcasts does not display its native transcript interface for a private RSS
feed followed by URL. The RSS includes a Podcasting 2.0 SRT reference and a
`Read the transcript` link to the plain-text file.
