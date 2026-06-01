from html import escape
from pathlib import Path
from typing import List, Tuple

from .config import require_env
from .subtitles import Boundary, estimated_boundaries, format_srt


class MockTTS:
    voice = "mock-voice"

    def synthesize(self, narration: str, audio_path: Path, subtitle_path: Path) -> int:
        duration = max(90, round(len(narration.split()) / 2.4))
        audio_path.write_bytes(b"MOCK MP3 FOR DRY RUN\n")
        subtitle_path.write_text(
            format_srt(estimated_boundaries(narration, duration)),
            encoding="utf-8",
        )
        return duration


class AzureTTS:
    def __init__(self, voice: str, rate_percent: int = -10):
        import azure.cognitiveservices.speech as speechsdk

        self.speechsdk = speechsdk
        self.voice = voice
        self.rate_percent = rate_percent
        speech_config = speechsdk.SpeechConfig(
            subscription=require_env("AZURE_SPEECH_KEY"),
            region=require_env("AZURE_SPEECH_REGION"),
        )
        speech_config.speech_synthesis_voice_name = voice
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3
        )
        self.speech_config = speech_config

    def synthesize(self, narration: str, audio_path: Path, subtitle_path: Path) -> int:
        speechsdk = self.speechsdk
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(audio_path))
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=audio_config,
        )
        boundaries: List[Boundary] = []

        def on_boundary(event) -> None:
            text = getattr(event, "text", "") or narration[
                event.text_offset : event.text_offset + event.word_length
            ]
            boundaries.append(
                Boundary(
                    text=text,
                    start_seconds=event.audio_offset / 10_000_000,
                    duration_seconds=max(getattr(event, "duration", 0) / 10_000_000, 0.1),
                )
            )

        synthesizer.synthesis_word_boundary.connect(on_boundary)
        result = synthesizer.speak_ssml_async(self._ssml(narration)).get()
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            details = speechsdk.SpeechSynthesisCancellationDetails.from_result(result)
            raise RuntimeError("Azure speech synthesis failed: {}".format(details.error_details))

        duration_seconds = max(1, round(result.audio_duration.total_seconds()))
        if not boundaries:
            boundaries = estimated_boundaries(narration, duration_seconds)
        subtitle_path.write_text(format_srt(boundaries), encoding="utf-8")
        return duration_seconds

    def _ssml(self, narration: str) -> str:
        return (
            "<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" "
            "xml:lang=\"en-US\"><voice name=\"{}\"><prosody rate=\"{}%\">{}</prosody>"
            "</voice></speak>"
        ).format(self.voice, self.rate_percent, escape(narration))
