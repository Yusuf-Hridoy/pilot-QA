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

---

## Day 4-5 — Planner
**Prompt:**
Build the Planner module for playwright-pilot.

Two files to create:

==========================================
FILE 1: src/playwright_pilot/prompts/planner.txt
==========================================

Create the file with this exact content (no extra wrapping):

You are an expert QA test planner.

Given a UserStory, produce a JSON ActionPlan with atomic, executable steps.

RULES:
- Each step performs exactly ONE action.
- Use natural-language descriptions in "target" fields (e.g. "the username input field", "the Login button"). NEVER write CSS selectors, XPath, or HTML.
- Include a "verify" step after every meaningful state change.
- The first step should usually be "navigate" to the target_url.
- Use action_type from this fixed set ONLY: "navigate", "click", "fill", "verify", "wait".
- For "fill" actions, the "value" field is required.
- For "verify" actions, the "verification" field is required and describes what should be true.
- Always respond in English.
- Respond with ONLY valid JSON matching the schema below. No prose, no markdown fences.

SCHEMA:
{
  "story": <the input UserStory unchanged>,
  "steps": [
    {
      "action_type": "navigate" | "click" | "fill" | "verify" | "wait",
      "target": "natural language description of the target element or URL",
      "value": "only required for fill actions",
      "verification": "only required for verify actions"
    }
  ]
}

INPUT USER STORY:
{story_json}

==========================================
FILE 2: src/playwright_pilot/planner.py
==========================================

Implement:

    class PlannerError(Exception): pass

    class Planner:
        def __init__(self) -> None: ...
        def plan(self, story: UserStory) -> ActionPlan: ...

Requirements:
- Import `chat` from playwright_pilot.llm_client
- Import UserStory, ActionPlan from playwright_pilot.models
- Load the prompt template from src/playwright_pilot/prompts/planner.txt at __init__ time. Use pathlib relative to this file's location, not cwd.
- In plan():
    1. Format the prompt by replacing {story_json} with story.model_dump_json()
    2. Build messages: [{"role": "system", "content": "You always respond in English with valid JSON only."}, {"role": "user", "content": formatted_prompt}]
    3. Call chat(messages, json_mode=True)
    4. Try to parse the response as JSON, then validate via ActionPlan.model_validate(parsed_dict)
    5. On failure (json.JSONDecodeError OR pydantic ValidationError), retry ONCE with a stricter system message: "Your previous response was invalid. You must respond with valid JSON only matching the requested schema. No prose, no markdown."
    6. After the second failure, raise PlannerError with the underlying exception chained via `raise ... from e`
- Return the validated ActionPlan
- Keep planner.py under 100 lines

==========================================
FILE 3: tests/test_planner.py
==========================================

Write 4 pytest cases. Use unittest.mock.patch to mock playwright_pilot.planner.chat (patch where it's imported, not where it's defined).

1. test_planner_returns_valid_action_plan
   Mock chat() to return a valid JSON string matching ActionPlan schema.
   Confirm Planner().plan(story) returns a correctly-typed ActionPlan with steps preserved.

2. test_planner_retries_once_on_invalid_json
   Mock chat() to return "not valid json" on first call, valid JSON on second call.
   Confirm chat is called exactly 2 times and plan returns successfully.

3. test_planner_raises_after_two_failures
   Mock chat() to return invalid JSON both times.
   Confirm PlannerError is raised.

4. test_planner_preserves_original_story
   Mock chat() to return a valid plan.
   Confirm returned ActionPlan.story equals the input story.

Constraints:
- No real API calls in tests
- No pytest fixtures needed for these 4 tests — keep them self-contained
- All comments and docstrings in English
- Do NOT import or use LangChain, LangGraph, or any agent framework

**Result:** ✅ 4 planner tests passed (13 total)
**Real LLM smoke test:** ✅ Mistral returned a valid plan
**Notes:**
- Had to fix a hardcoded `alias python="..."` in ~/.zshrc that broke venv activation; replaced with a shell function that checks $VIRTUAL_ENV
- Mistral produced clean JSON, respected the schema, used natural-language targets, included navigate as first step, and added verify steps after state changes
