from unittest.mock import MagicMock, patch

import httpx
import ollama
import pytest

from dockerfile_generator.generator import (
    DockerfileGenerationError,
    build_prompt,
    clean_output,
    generate_dockerfile,
)


def test_build_prompt_includes_language():
    prompt = build_prompt("Java")
    assert "Java" in prompt
    assert "Dockerfile" in prompt


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("FROM python:3.12\nCMD [\"python\", \"app.py\"]", "FROM python:3.12\nCMD [\"python\", \"app.py\"]\n"),
        ("```dockerfile\nFROM python:3.12\n```", "FROM python:3.12\n"),
        ("```\nFROM python:3.12\n```\n", "FROM python:3.12\n"),
        ("  FROM python:3.12  \n", "FROM python:3.12\n"),
    ],
)
def test_clean_output_strips_fences_and_whitespace(raw, expected):
    assert clean_output(raw) == expected


def test_generate_dockerfile_rejects_empty_language():
    with pytest.raises(ValueError):
        generate_dockerfile("   ")


@patch("dockerfile_generator.generator.ollama.Client")
def test_generate_dockerfile_returns_cleaned_content(mock_client_cls):
    mock_client = MagicMock()
    mock_client.chat.return_value = {"message": {"content": "```\nFROM python:3.12\n```"}}
    mock_client_cls.return_value = mock_client

    result = generate_dockerfile("python", model="llama3.2", timeout=5.0)

    assert result == "FROM python:3.12\n"
    mock_client_cls.assert_called_once_with(host=None, timeout=5.0)
    mock_client.chat.assert_called_once()
    assert mock_client.chat.call_args.kwargs["model"] == "llama3.2"


@patch("dockerfile_generator.generator.ollama.Client")
def test_generate_dockerfile_maps_connection_error(mock_client_cls):
    mock_client = MagicMock()
    mock_client.chat.side_effect = ConnectionError("boom")
    mock_client_cls.return_value = mock_client

    with pytest.raises(DockerfileGenerationError, match="Ollama"):
        generate_dockerfile("python")


@patch("dockerfile_generator.generator.ollama.Client")
def test_generate_dockerfile_maps_timeout(mock_client_cls):
    mock_client = MagicMock()
    mock_client.chat.side_effect = httpx.ReadTimeout("boom")
    mock_client_cls.return_value = mock_client

    with pytest.raises(DockerfileGenerationError, match="Timed out"):
        generate_dockerfile("python", timeout=1.0)


@patch("dockerfile_generator.generator.ollama.Client")
def test_generate_dockerfile_maps_model_not_found(mock_client_cls):
    mock_client = MagicMock()
    mock_client.chat.side_effect = ollama.ResponseError("model not found", status_code=404)
    mock_client_cls.return_value = mock_client

    with pytest.raises(DockerfileGenerationError, match="ollama pull llama3.2"):
        generate_dockerfile("python", model="llama3.2")


@patch("dockerfile_generator.generator.ollama.Client")
def test_generate_dockerfile_maps_other_response_error(mock_client_cls):
    mock_client = MagicMock()
    mock_client.chat.side_effect = ollama.ResponseError("something else broke", status_code=500)
    mock_client_cls.return_value = mock_client

    with pytest.raises(DockerfileGenerationError, match="something else broke"):
        generate_dockerfile("python")
