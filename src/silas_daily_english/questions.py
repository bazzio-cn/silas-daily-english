import json
from typing import List

from .models import DiscussionQuestion, Story


class MockQuestionGenerator:
    def generate(self, story: Story) -> List[DiscussionQuestion]:
        return [
            DiscussionQuestion(
                question="Why did Daniel visit the hospital?",
                answer_hint="He wanted to visit his uncle after the operation.",
            ),
            DiscussionQuestion(
                question="How did the nurse help Daniel feel better?",
                answer_hint="She told him that his uncle was doing very well.",
            ),
            DiscussionQuestion(
                question="What message did Daniel's uncle ask him to write down?",
                answer_hint="Everything is all right.",
            ),
        ]


class OpenAIQuestionGenerator:
    def __init__(self, model: str = "gpt-5-mini"):
        from openai import OpenAI

        self.client = OpenAI()
        self.model = model

    def generate(self, story: Story) -> List[DiscussionQuestion]:
        response = self.client.responses.create(
            model=self.model,
            input=_build_prompt(story),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "daily_english_questions",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "questions": {
                                "type": "array",
                                "minItems": 3,
                                "maxItems": 3,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "question": {"type": "string"},
                                        "answer_hint": {"type": "string"},
                                    },
                                    "required": ["question", "answer_hint"],
                                    "additionalProperties": False,
                                },
                            }
                        },
                        "required": ["questions"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        payload = json.loads(response.output_text)
        return [
            DiscussionQuestion(
                question=item["question"].strip(),
                answer_hint=item["answer_hint"].strip(),
            )
            for item in payload["questions"]
        ]


def render_questions_email(story: Story, questions: List[DiscussionQuestion]) -> str:
    lines = [
        story.title,
        "",
        "Three small questions for today's listening chat:",
        "",
    ]
    for index, question in enumerate(questions, start=1):
        lines.append("{}. {}".format(index, question.question))
        lines.append("   Hint: {}".format(question.answer_hint))
    lines.extend(
        [
            "",
            "Story text:",
            "",
            story.body,
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _build_prompt(story: Story) -> str:
    return """Create exactly three short parent-facing comprehension or discussion
questions about this English listening story. The questions are for an adult to
ask an 11-year-old after listening. Keep each question natural, concrete, and
easy to answer from the story. Include a brief answer hint for the adult. Do not
refer to the learning system, podcast feed, or OpenAI. Return only JSON.

Title:
{title}

Story:
{body}
""".format(
        title=story.title,
        body=story.body,
    )
