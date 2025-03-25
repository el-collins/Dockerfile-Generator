"""Prompt construction, the Ollama call, and output cleanup."""

from __future__ import annotations

import httpx
import ollama

DEFAULT_MODEL = "llama3.2"
DEFAULT_TIMEOUT = 120.0

PROMPT_TEMPLATE = """Generate an ideal Dockerfile for a {language} application, following best practices.

Do not provide any description or explanation - only output the Dockerfile contents.

Make sure to include:
- an appropriate base image
- installing dependencies
- setting up a working directory
- adding the source code
- running the application
"""


class DockerfileGenerationError(Exception):
    """Raised when a Dockerfile could not be generated."""


def build_prompt(language: str) -> str:
    return PROMPT_TEMPLATE.format(language=language)


def clean_output(text: str) -> str:
    """Strip a leading/trailing ``` markdown fence, if the model added one."""
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip() + "\n"


def generate_dockerfile(
    language: str,
    *,
    model: str = DEFAULT_MODEL,
    host: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    language = language.strip()
    if not language:
        raise ValueError("language must not be empty")

    client = ollama.Client(host=host, timeout=timeout)

    try:
        response = client.chat(
            model=model,
            messages=[{"role": "user", "content": build_prompt(language)}],
        )
    except ConnectionError as exc:
        raise DockerfileGenerationError(
            f"Could not reach Ollama at {host or 'the default host'}. "
            "Make sure Ollama is installed and running: https://ollama.com"
        ) from exc
    except httpx.TimeoutException as exc:
        raise DockerfileGenerationError(
            f"Timed out waiting for Ollama after {timeout:g}s. "
            "Try a smaller model or pass --timeout with a larger value."
        ) from exc
    except ollama.ResponseError as exc:
        if exc.status_code == 404:
            raise DockerfileGenerationError(
                f"Model '{model}' is not available locally. Pull it first with: ollama pull {model}"
            ) from exc
        raise DockerfileGenerationError(f"Ollama returned an error: {exc.error}") from exc

    return clean_output(response["message"]["content"])
