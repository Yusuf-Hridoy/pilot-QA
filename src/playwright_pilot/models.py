from typing import Literal

from pydantic import BaseModel, Field, model_validator


class UserStory(BaseModel):
    goal: str = Field(..., description="High-level objective of the user story")
    actions: list[str] = Field(..., description="Sequence of actions to perform")
    expected_outcomes: list[str] = Field(..., description="Expected results after completing the story")
    target_url: str | None = Field(None, description="Optional starting URL for the story")


class PlannedAction(BaseModel):
    action_type: Literal["navigate", "click", "fill", "verify", "wait"] = Field(
        ..., description="Type of action to perform"
    )
    target: str = Field(..., description="Natural language description of the target element")
    value: str | None = Field(None, description="Value to input or use with the action")
    verification: str | None = Field(None, description="Natural language verification criteria")

    @model_validator(mode="after")
    def check_fill_has_value(self) -> "PlannedAction":
        if self.action_type == "fill" and not self.value:
            raise ValueError("fill actions must provide a non-empty value")
        return self


class ActionPlan(BaseModel):
    story: UserStory = Field(..., description="User story this plan executes")
    steps: list[PlannedAction] = Field(..., description="Ordered list of planned actions")

    @model_validator(mode="after")
    def check_steps_not_empty(self) -> "ActionPlan":
        if not self.steps:
            raise ValueError("steps must not be empty")
        return self
