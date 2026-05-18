# Kimi Code Agent prompts log

This file logs every prompt I gave to Kimi Code Agent while building playwright-pilot.

---

## Day 1 — Project scaffolding
**Prompt:**
Create a Python project called playwright-pilot.

Structure:
- pyproject.toml using hatchling, Python 3.11+
- Dependencies: playwright>=1.45, openai>=1.50, pydantic>=2.0, click>=8.0, rich>=13.0, python-dotenv>=1.0
- Dev dependencies: pytest>=8.0, pytest-asyncio>=0.23, ruff>=0.6
- Folder layout:
  src/playwright_pilot/__init__.py
  src/playwright_pilot/prompts/  (empty folder, add .gitkeep)
  tests/__init__.py
  examples/
- .env.example with these keys:
    MISTRAL_API_KEY=
    MISTRAL_BASE_URL=https://api.mistral.ai/v1
    MISTRAL_PLANNER_MODEL=mistral-large-latest
    MISTRAL_VERIFIER_MODEL=mistral-small-latest
    MISTRAL_VISION_MODEL=pixtral-12b-2409
- .gitignore standard Python (include .env, .venv, __pycache__, .pytest_cache, dist, build)
- LICENSE: MIT, copyright "Yusuf"
- README.md (placeholder with title and one-line description, full version coming separately)

Do NOT add: docker, async frameworks, web UI scaffolding, database libs, langchain, langgraph, requests library, httpx.

Output the file contents and folder commands only. No explanations.

**Result:** ✅ worked / ❌ had to fix X
**Notes:**

---

## Day 2 — Pydantic models
**Prompt:**
In src/playwright_pilot/models.py, define these pydantic v2 models:

1. UserStory:
   - goal: str
   - actions: list[str]
   - expected_outcomes: list[str]
   - target_url: str | None = None

2. PlannedAction:
   - action_type: Literal["navigate", "click", "fill", "verify", "wait"]
   - target: str  (natural language description, NOT a CSS selector)
   - value: str | None = None
   - verification: str | None = None

3. ActionPlan:
   - story: UserStory
   - steps: list[PlannedAction]

Rules:
- Use Field(..., description="...") for each field
- Add a model_validator (mode="after") on PlannedAction: if action_type == "fill", value must be provided (non-empty string)
- Add a model_validator (mode="after") on ActionPlan: steps must not be empty

Then in tests/test_models.py, write 4 pytest cases:
1. test_valid_user_story_creates_successfully
2. test_fill_action_without_value_raises_validation_error
3. test_empty_action_plan_steps_raises_validation_error
4. test_models_serialize_to_json

Constraints:
- Pure pydantic v2, no external dependencies
- Keep models.py under 100 lines
- Readable code, no metaprogramming, no inheritance hierarchies
- Use `from typing import Literal` and `from pydantic import BaseModel, Field, model_validator`
- All comments and docstrings in English

**Result:** ✅ worked / ❌ had to fix X
**Notes:**
---

## Day 3 — Parser
**Prompt:**
In src/playwright_pilot/parser.py, write a parser that converts plain English ticket text into a UserStory model.

Public API:
    parse_ticket(text: str) -> UserStory

Also define:
    class ParseError(Exception): pass

Rules:
- Pure Python only — no LLM calls, no API calls, no external libraries beyond stdlib and pydantic
- Import UserStory from playwright_pilot.models
- Accept TWO input styles:

  Style A (structured) — text contains sections like:
      Goal: <one line>
      URL: <one line, optional>
      Steps:
        - step one
        - step two
      Verify:
        - outcome one
        - outcome two

  Style B (loose prose) — plain paragraphs.
      For loose prose: split on sentences (use simple "." or newline splitting, no nltk).
      The first sentence is the goal.
      Remaining sentences become actions.
      Any sentence containing "verify", "should", "must", or "ensure" goes into expected_outcomes.

- URL extraction: scan the entire text for any http:// or https:// URL using a simple regex. If found, set target_url.

- Raise ParseError with a helpful message if:
    * text is empty or only whitespace
    * goal cannot be determined (no Goal: section and no parseable first sentence)
    * actions list is empty after parsing

- Return a populated UserStory model. Use model validation (pydantic will catch invalid data automatically).

Then in tests/test_parser.py, write 5 pytest cases:

1. test_structured_input_parses_all_sections
   Input has Goal, URL, Steps, Verify sections. Confirm all four fields populated correctly.

2. test_loose_prose_parses_correctly
   Input is a single paragraph. Confirm goal is first sentence, actions and outcomes split sensibly.

3. test_empty_input_raises_parse_error
   parse_ticket("") and parse_ticket("   ") both raise ParseError.

4. test_url_extracted_from_text
   Input contains "https://opensource-demo.orangehrmlive.com" somewhere. Confirm target_url is set.

5. test_input_with_no_actions_raises_parse_error
   Input has a goal but no steps. Confirm ParseError is raised.

Constraints:
- Keep parser.py under 100 lines
- Readable code — no clever regex tricks, no list comprehensions nested more than one level deep
- Use only: re, typing, playwright_pilot.models
- All docstrings and comments in English
- Function should have a clear docstring with examples

**Result:** ✅ 5 parser tests passed (9 total)
**Notes:**
- Needed `pip install -e .` so the package was importable from the venv
- User's shell had pyenv overriding the venv `python`, so `.venv/bin/python` was needed
