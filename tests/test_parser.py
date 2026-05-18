import pytest

from playwright_pilot.parser import ParseError, parse_ticket


def test_structured_input_parses_all_sections():
    text = """Goal: Log in to the app
URL: https://example.com
Steps:
  - Go to login page
  - Enter credentials
  - Click submit
Verify:
  - Dashboard loads
  - Welcome message appears"""
    story = parse_ticket(text)
    assert story.goal == "Log in to the app"
    assert story.target_url == "https://example.com"
    assert story.actions == ["Go to login page", "Enter credentials", "Click submit"]
    assert story.expected_outcomes == ["Dashboard loads", "Welcome message appears"]


def test_loose_prose_parses_correctly():
    text = (
        "Log in to the app. Enter your username and password. "
        "Click the submit button. Verify the dashboard loads."
    )
    story = parse_ticket(text)
    assert story.goal == "Log in to the app"
    assert "Enter your username and password" in story.actions
    assert "Click the submit button" in story.actions
    assert any("dashboard loads" in o.lower() for o in story.expected_outcomes)


def test_empty_input_raises_parse_error():
    with pytest.raises(ParseError, match="empty"):
        parse_ticket("")
    with pytest.raises(ParseError, match="empty"):
        parse_ticket("   ")


def test_url_extracted_from_text():
    text = (
        "Go to https://opensource-demo.orangehrmlive.com and log in. "
        "Enter credentials. Verify login succeeds."
    )
    story = parse_ticket(text)
    assert story.target_url == "https://opensource-demo.orangehrmlive.com"


def test_input_with_no_actions_raises_parse_error():
    text = "Goal: Just sit there"
    with pytest.raises(ParseError, match="No actions"):
        parse_ticket(text)
