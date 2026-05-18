import json
from unittest.mock import patch

import pytest

from playwright_pilot.models import ActionPlan, PlannedAction, UserStory
from playwright_pilot.planner import Planner, PlannerError


def _valid_plan_dict(story: UserStory) -> dict:
    return {
        "story": story.model_dump(),
        "steps": [
            {
                "action_type": "navigate",
                "target": "https://example.com",
                "value": None,
                "verification": None,
            },
            {
                "action_type": "fill",
                "target": "the username field",
                "value": "admin",
                "verification": None,
            },
        ],
    }


def test_planner_returns_valid_action_plan():
    story = UserStory(
        goal="Log in",
        actions=["Go to page", "Enter username"],
        expected_outcomes=["Logged in"],
        target_url="https://example.com",
    )
    plan_dict = _valid_plan_dict(story)
    with patch("playwright_pilot.planner.chat", return_value=json.dumps(plan_dict)) as mock_chat:
        planner = Planner()
        result = planner.plan(story)
        mock_chat.assert_called_once()
    assert isinstance(result, ActionPlan)
    assert len(result.steps) == 2
    assert result.steps[0].action_type == "navigate"


def test_planner_retries_once_on_invalid_json():
    story = UserStory(
        goal="Log in",
        actions=["Go to page"],
        expected_outcomes=["Logged in"],
        target_url="https://example.com",
    )
    plan_dict = _valid_plan_dict(story)
    with patch(
        "playwright_pilot.planner.chat", side_effect=["not valid json", json.dumps(plan_dict)]
    ) as mock_chat:
        planner = Planner()
        result = planner.plan(story)
        assert mock_chat.call_count == 2
    assert isinstance(result, ActionPlan)


def test_planner_raises_after_two_failures():
    story = UserStory(
        goal="Log in",
        actions=["Go to page"],
        expected_outcomes=["Logged in"],
        target_url="https://example.com",
    )
    with patch("playwright_pilot.planner.chat", return_value="not valid json") as mock_chat:
        planner = Planner()
        with pytest.raises(PlannerError):
            planner.plan(story)
        assert mock_chat.call_count == 2


def test_planner_preserves_original_story():
    story = UserStory(
        goal="Log in",
        actions=["Go to page", "Enter username"],
        expected_outcomes=["Logged in"],
        target_url="https://example.com",
    )
    plan_dict = _valid_plan_dict(story)
    with patch("playwright_pilot.planner.chat", return_value=json.dumps(plan_dict)):
        planner = Planner()
        result = planner.plan(story)
    assert result.story == story
