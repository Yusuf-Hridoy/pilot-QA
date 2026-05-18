import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from rich import print

from playwright_pilot.models import ActionPlan, PlannedAction


class ExplorerError(Exception):
    """Base exception for Explorer errors."""


class ActionExecutionError(ExplorerError):
    """Raised when a single action step fails."""


@dataclass
class StepResult:
    step_index: int
    action: PlannedAction
    success: bool
    screenshot_path: Path | None
    error_message: str | None = None
    dom_snapshot: str | None = None


@dataclass
class RunResult:
    plan: ActionPlan
    step_results: list[StepResult]
    all_passed: bool
    artifacts_dir: Path


class Explorer:
    """Execute an ActionPlan in a browser and collect results."""

    def __init__(
        self,
        headless: bool = True,
        artifacts_dir: Path | None = None,
        timeout_ms: int = 30_000,
    ) -> None:
        self.headless = headless
        self.timeout_ms = timeout_ms
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.artifacts_dir = artifacts_dir or Path("artifacts") / timestamp
        self.screenshots_dir = self.artifacts_dir / "screenshots"

    def run(self, plan: ActionPlan) -> RunResult:
        """Execute the plan and return collected results."""
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        step_results: list[StepResult] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()
            page.set_default_timeout(self.timeout_ms)

            for idx, step in enumerate(plan.steps):
                screenshot_path = self.screenshots_dir / f"step_{idx:02d}_{step.action_type}.png"
                success = True
                error_msg: str | None = None

                try:
                    self._execute_action(page, step, plan)
                except ActionExecutionError as e:
                    success = False
                    error_msg = str(e)
                    print(f"[red]{error_msg}[/red]")
                except Exception as e:
                    success = False
                    error_msg = f"Step {idx} ({step.action_type}) unexpected error: {e}"
                    print(f"[red]{error_msg}[/red]")

                try:
                    page.screenshot(path=str(screenshot_path))
                except Exception:
                    screenshot_path = None

                try:
                    dom_snapshot = page.content()
                except Exception:
                    dom_snapshot = None

                step_results.append(
                    StepResult(
                        step_index=idx,
                        action=step,
                        success=success,
                        screenshot_path=screenshot_path,
                        error_message=error_msg,
                        dom_snapshot=dom_snapshot,
                    )
                )

                if not success:
                    break

            browser.close()

        all_passed = all(r.success for r in step_results)
        return RunResult(
            plan=plan,
            step_results=step_results,
            all_passed=all_passed,
            artifacts_dir=self.artifacts_dir,
        )

    def _execute_action(self, page: Any, step: PlannedAction, plan: ActionPlan) -> None:
        action_type = step.action_type
        target = step.target
        value = step.value

        try:
            if action_type == "navigate":
                url = target if target.startswith(("http://", "https://")) else plan.story.target_url
                if not url:
                    raise ActionExecutionError("No URL provided for navigate action")
                page.goto(url)
            elif action_type == "click":
                locator = self._resolve_locator(page, target, "click")
                locator.click()
            elif action_type == "fill":
                locator = self._resolve_locator(page, target, "fill")
                if value is None:
                    raise ActionExecutionError(f"No value provided for fill action on '{target}'")
                locator.fill(value)
            elif action_type == "verify":
                # TODO: Implement LLM-based verification in Day 7-9
                _ = page.content()
            elif action_type == "wait":
                page.wait_for_load_state("networkidle")
            else:
                raise ActionExecutionError(f"Unknown action type: {action_type}")
        except PlaywrightTimeoutError as e:
            raise ActionExecutionError(
                f"Timeout executing {action_type} on '{target}': {e}"
            ) from e
        except ActionExecutionError:
            raise
        except Exception as e:
            raise ActionExecutionError(
                f"Error executing {action_type} on '{target}': {e}"
            ) from e

    def _resolve_locator(self, page: Any, target: str, action_type: str) -> Any:
        candidates = [target, self._clean_target(target)]
        seen = set()

        for candidate in candidates:
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)

            if action_type == "click":
                locators = [
                    page.get_by_role("button", name=candidate),
                    page.get_by_role("link", name=candidate),
                    page.get_by_text(candidate, exact=False),
                ]
            elif action_type == "fill":
                locators = [
                    page.get_by_label(candidate),
                    page.get_by_placeholder(candidate),
                    page.get_by_role("textbox", name=candidate),
                ]
            else:
                locators = []

            for locator in locators:
                if locator.count() == 1:
                    return locator

        raise ActionExecutionError(f"Could not resolve target: {target}")

    def _clean_target(self, target: str) -> str:
        lower = target.lower()
        fillers = [
            "the ", " a ", " an ",
            " input field", " field", " input",
            " button", " link",
            " page",
        ]
        for f in fillers:
            lower = lower.replace(f, " ")
        return lower.strip()
