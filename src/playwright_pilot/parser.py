import re
from playwright_pilot.models import UserStory

class ParseError(Exception):
    """Raised when ticket text cannot be parsed into a UserStory."""


URL_RE = re.compile(r"https?://[^\s]+")

def parse_ticket(text: str) -> UserStory:
    """Convert plain English ticket text into a UserStory model.

    Supports structured tickets with Goal, URL, Steps and Verify sections,
    as well as loose prose paragraphs.

    Examples:
        >>> parse_ticket("Goal: Login\\nSteps:\\n  - Go to page")
        UserStory(goal="Login", ...)
        >>> parse_ticket("Log in to the app. Click submit. Verify dashboard loads.")
        UserStory(goal="Log in to the app", ...)
    """
    if not text or not text.strip():
        raise ParseError("Input text is empty or whitespace only.")
    target_url = _extract_url(text)
    if _is_structured(text):
        goal, actions, outcomes = _parse_structured(text)
    else:
        goal, actions, outcomes = _parse_prose(text)
    if not goal:
        raise ParseError("Could not determine goal from input text.")
    if not actions:
        raise ParseError("No actions found in input text.")
    explicit_url = _extract_explicit_url(text)
    if explicit_url:
        target_url = explicit_url
    return UserStory(
        goal=goal, actions=actions, expected_outcomes=outcomes, target_url=target_url
    )

def _extract_url(text: str) -> str | None:
    match = URL_RE.search(text)
    return match.group(0) if match else None

def _extract_explicit_url(text: str) -> str | None:
    for line in text.splitlines():
        if line.strip().lower().startswith("url:"):
            return line.split(":", 1)[1].strip()
    return None

def _is_structured(text: str) -> bool:
    lower = text.lower()
    return "goal:" in lower and ("steps:" in lower or "verify:" in lower)

def _parse_structured(text: str) -> tuple[str, list[str], list[str]]:
    goal = ""
    actions: list[str] = []
    outcomes: list[str] = []
    lines = text.splitlines()
    current_section: str | None = None
    for raw in lines:
        line = raw.strip()
        lower = line.lower()
        if lower.startswith("goal:"):
            goal = line.split(":", 1)[1].strip()
            current_section = None
        elif lower.startswith("url:"):
            current_section = None
        elif lower.startswith("steps:"):
            current_section = "steps"
        elif lower.startswith("verify:"):
            current_section = "verify"
        elif line.startswith("-") or line.startswith("*"):
            item = line.lstrip("-* ").strip()
            if current_section == "steps":
                actions.append(item)
            elif current_section == "verify":
                outcomes.append(item)
        elif line and current_section in ("steps", "verify"):
            if current_section == "steps":
                actions.append(line)
            else:
                outcomes.append(line)
    return goal, actions, outcomes

def _parse_prose(text: str) -> tuple[str, list[str], list[str]]:
    raw_parts = re.split(r"[.\n]+", text)
    sentences = [s.strip() for s in raw_parts if s.strip()]
    if not sentences:
        return "", [], []
    goal = sentences[0]
    actions: list[str] = []
    outcomes: list[str] = []
    for sentence in sentences[1:]:
        lower = sentence.lower()
        if any(word in lower for word in ("verify", "should", "must", "ensure")):
            outcomes.append(sentence)
        else:
            actions.append(sentence)
    return goal, actions, outcomes
