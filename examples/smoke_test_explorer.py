"""Day 6 smoke test: parser → planner → explorer end-to-end on Sauce Demo."""
from rich import print
from playwright_pilot.parser import parse_ticket
from playwright_pilot.planner import Planner
from playwright_pilot.explorer import Explorer

ticket = """
Goal: Log into Sauce Demo
URL: https://www.saucedemo.com/
Steps:
  - Enter standard_user in the Username field
  - Enter secret_sauce in the Password field
  - Click the Login button
Verify:
  - Products page is visible
"""

story = parse_ticket(ticket)
plan = Planner().plan(story)
print("[bold green]Plan generated[/bold green]")
print(plan.model_dump_json(indent=2))

print("[bold yellow]Running Explorer (headless=False so you can watch)...[/bold yellow]")
result = Explorer(headless=False).run(plan)

print(f"[bold]All passed:[/bold] {result.all_passed}")
print(f"[bold]Artifacts:[/bold] {result.artifacts_dir}")
for sr in result.step_results:
    status = "✅" if sr.success else "❌"
    print(f"  {status} Step {sr.step_index}: {sr.action.action_type} → {sr.action.target}")
    if sr.error_message:
        print(f"     [red]{sr.error_message}[/red]")
