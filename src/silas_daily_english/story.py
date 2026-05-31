import json
from typing import Iterable, List

from .models import Story


MOCK_STORY = Story(
    title="The Message at the Hospital",
    body=(
        "On Monday afternoon, Daniel went to a small hospital to visit his uncle. "
        "His uncle had an operation that morning, and everyone wanted to know if it "
        "had been successful. Daniel arrived early, but the doctor was still busy. "
        "A nurse asked him to wait in a quiet room near the front desk.\n\n"
        "Daniel sat down and opened a book. Across the room, another patient was "
        "talking to his daughter. A few minutes later, the telephone rang. The nurse "
        "answered it, listened carefully, and wrote a short message on a piece of "
        "paper. Then she walked towards Daniel with a smile.\n\n"
        "\"Your uncle is doing very well,\" she said. \"The doctor will speak to you "
        "after he has finished his work.\"\n\n"
        "Daniel felt much better. He sent a message to his family at once. While he "
        "was waiting, he went downstairs to buy a cup of tea. When he returned, his "
        "uncle was awake and cheerful.\n\n"
        "\"I was not alone for long,\" his uncle said. \"The nurses have been very "
        "kind.\"\n\n"
        "Before Daniel left, his uncle gave him a small notebook. \"Bring it back "
        "tomorrow,\" he said. \"I want you to write down the following words: "
        "everything is all right.\"\n\n"
        "Daniel smiled. It was the best message he had received all day. On his "
        "way home, the streets looked brighter than before, and the journey felt "
        "surprisingly short."
    ),
)


class MockStoryGenerator:
    def generate(
        self,
        lesson: int,
        daily_focus_words: Iterable[str],
        learned_words: Iterable[str],
        attempt: int,
    ) -> Story:
        return MOCK_STORY


class OpenAIStoryGenerator:
    def __init__(self, model: str = "gpt-5-mini"):
        from openai import OpenAI

        self.client = OpenAI()
        self.model = model

    def generate(
        self,
        lesson: int,
        daily_focus_words: Iterable[str],
        learned_words: Iterable[str],
        attempt: int,
    ) -> Story:
        prompt = _build_prompt(
            lesson,
            list(daily_focus_words),
            list(learned_words),
            attempt,
        )
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "daily_english_story",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "body": {"type": "string"},
                        },
                        "required": ["title", "body"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        payload = json.loads(response.output_text)
        return Story(title=payload["title"].strip(), body=payload["body"].strip())


def _build_prompt(
    lesson: int,
    daily_focus_words: List[str],
    learned_words: List[str],
    attempt: int,
) -> str:
    return """Write one original English listening story for an 11-year-old Year 6
student who is learning English. The student has memorised New Concept English 2
through lesson {lesson}. Write 220-290 words in British English. Keep the story
clear, warm, and interesting without sounding childish. Ordinary primary-school
English vocabulary is allowed by default. The textbook list is not a strict
whitelist. Naturally use at least two of today's focus words:
{daily_focus_words}

Previously introduced textbook words may also be used when they fit naturally:
{learned_words}

Do not copy, closely paraphrase, or continue any textbook passage. Do not mention
the textbook or the learning task. Return only the requested JSON object.
Generation attempt: {attempt}.
""".format(
        lesson=lesson,
        daily_focus_words=", ".join(daily_focus_words) or "(no new words listed)",
        learned_words=", ".join(learned_words) or "(no prior words listed)",
        attempt=attempt,
    )
