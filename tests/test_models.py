import json

import pytest
from pydantic import ValidationError

from playwright_pilot.models import ActionPlan, PlannedAction, UserStory


def test_valid_user_story_creates_successfully():
    story = UserStory(
        goal="Log into the dashboard",
        actions=["Open login page", "Enter credentials", "Submit form"],
        expected_outcomes=["User is authenticated", "Dashboard is displayed"],
        target_url="https://example.com/login",
    )
    assert story.goal == "Log into the dashboard"
    assert len(story.actions) == 3
    assert story.target_url == "https://example.com/login"


def test_fill_action_without_value_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        PlannedAction(action_type="fill", target="Username field")
    assert "fill actions must provide a non-empty value" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        PlannedAction(action_type="fill", target="Username field", value="")
    assert "fill actions must provide a non-empty value" in str(exc_info.value)


def test_empty_action_plan_steps_raises_validation_error():
    story = UserStory(
        goal="Navigate home",
        actions=["Click home"],
        expected_outcomes=["Home page loads"],
    )
    with pytest.raises(ValidationError) as exc_info:
        ActionPlan(story=story, steps=[])
    assert "steps must not be empty" in str(exc_info.value)


def test_models_serialize_to_json():
    story = UserStory(
        goal="Search for items",
        actions=["Click search", "Type query"],
        expected_outcomes=["Results shown"],
    )
    action = PlannedAction(action_type="click", target="Search button")
    plan = ActionPlan(story=story, steps=[action])

    story_json = story.model_dump_json()
    action_json = action.model_dump_json()
    plan_json = plan.model_dump_json()

    assert json.loads(story_json)["goal"] == "Search for items"
    assert json.loads(action_json)["action_type"] == "click"
    assert json.loads(plan_json)["story"]["goal"] == "Search for items"
    assert len(json.loads(plan_json)["steps"]) == 1
