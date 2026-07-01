"""Qwen Cloud client"""
import json
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from app.config import settings

client = OpenAI(
    api_key=settings.dashscope_api_key,
    base_url=settings.dashscope_base_url,
    timeout=120.0,   # generation can be slow; fail rather than hang forever
    max_retries=2,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


def _strip_fences(text: str) -> str:
    """Remove a leading ```json (or ```) fence and a trailing ``` fence."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        newline = cleaned.find("\n")
        start = newline + 1 if newline != -1 else 3
        cleaned = cleaned[start:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def chat(prompt: str, *, model: str | None = None, system: str | None = None) -> str:
    """Send a single-turn prompt to Qwen and return the text reply."""
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    completion = client.chat.completions.create(
        model=model or settings.text_model,
        messages=messages,
    )
    return completion.choices[0].message.content or ""


def chat_json(
    prompt: str,
    schema: type[ModelT],
    *,
    model: str | None = None,
    system: str | None = None,
    temperature: float = 0.7,
    max_attempts: int = 2,
) -> ModelT:
    """Call the model and validate its reply against a pydantic schema.

    Uses JSON mode. If the reply does not parse or fails validation, the error
    is fed back so the model can correct itself, up to max_attempts.
    """
    system_text = (
        (system or "You are a precise assistant.")
        + "\n\nReturn ONLY a single valid JSON object. No prose, no markdown."
    )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_text},
        {"role": "user", "content": prompt},
    ]

    last_error = ""
    for _ in range(max_attempts):
        completion = client.chat.completions.create(
            model=model or settings.text_model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        raw = completion.choices[0].message.content or ""
        try:
            return schema.model_validate(json.loads(_strip_fences(raw)))
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = str(exc)
            messages.append({"role": "assistant", "content": raw})
            messages.append(
                {
                    "role": "user",
                    "content": f"That was not valid. Error:\n{last_error}\nReturn corrected JSON only.",
                }
            )

    raise ValueError(
        f"Could not get valid {schema.__name__} after {max_attempts} attempts. Last error: {last_error}"
    )
