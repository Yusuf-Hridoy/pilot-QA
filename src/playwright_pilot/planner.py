import json
from pathlib import Path

from pydantic import ValidationError

from playwright_pilot.llm_client import chat
from playwright_pilot.models import ActionPlan, UserStory


class PlannerError(Exception):
    """Raised when planning fails after retries."""


class Planner:
    """Convert a UserStory into an executable ActionPlan via LLM."""

    def __init__(self) -> None:
        prompt_path = Path(__file__).with_name("prompts") / "planner.txt"
        self._template = prompt_path.read_text(encoding="utf-8")

    def plan(self, story: UserStory) -> ActionPlan:
        formatted = self._template.replace("{story_json}", story.model_dump_json())
        messages = [
            {"role": "system", "content": "You always respond in English with valid JSON only."},
            {"role": "user", "content": formatted},
        ]
        return self._try_plan(messages)

    def _try_plan(self, messages: list[dict]) -> ActionPlan:
        for attempt in range(2):
            try:
                raw = chat(messages, json_mode=True)
                parsed = json.loads(raw)
                return ActionPlan.model_validate(parsed)
            except (json.JSONDecodeError, ValidationError) as e:
                if attempt == 0:
                    messages[0]["content"] = (
                        "Your previous response was invalid. You must respond with valid JSON only "
                        "matching the requested schema. No prose, no markdown."
                    )
                    continue
                raise PlannerError("Failed to generate a valid action plan after retry.") from e
        raise PlannerError("Failed to generate a valid action plan after retry.")
