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