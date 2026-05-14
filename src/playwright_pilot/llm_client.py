"""Mistral LLM client wrapper. OpenAI-compatible interface for easy provider swap."""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client pointed at Mistral."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY not set. Copy .env.example to .env.")
    return OpenAI(
        api_key=api_key,
        base_url=os.environ.get("MISTRAL_BASE_URL", "https://api.mistral.ai/v1"),
    )


def chat(
    messages: list[dict],
    model: str | None = None,
    json_mode: bool = False,
    temperature: float = 0.2,
) -> str:
    """Send a chat completion. Returns the assistant's text content."""
    client = get_client()
    kwargs = {
        "model": model or os.environ.get("MISTRAL_PLANNER_MODEL", "mistral-large-latest"),
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""