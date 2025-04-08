from unittest.mock import patch

from dockerfile_generator.cli import main
from dockerfile_generator.generator import DockerfileGenerationError


def test_main_prints_to_stdout(capsys):
    with patch("dockerfile_generator.cli.generate_dockerfile", return_value="FROM python:3.12\n"):
        exit_code = main(["python"])

    assert exit_code == 0
    assert "FROM python:3.12" in capsys.readouterr().out


def test_main_writes_to_output_file(tmp_path):
    output_path = tmp_path / "Dockerfile"
    with patch("dockerfile_generator.cli.generate_dockerfile", return_value="FROM python:3.12\n"):
        exit_code = main(["python", "-o", str(output_path)])

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "FROM python:3.12\n"


def test_main_rejects_empty_language(capsys):
    exit_code = main(["   "])

    assert exit_code == 1
    assert "must not be empty" in capsys.readouterr().err


def test_main_falls_back_to_interactive_prompt(capsys):
    with (
        patch("builtins.input", return_value="java"),
        patch("dockerfile_generator.cli.generate_dockerfile", return_value="FROM eclipse-temurin:21\n") as mock_gen,
    ):
        exit_code = main([])

    assert exit_code == 0
    mock_gen.assert_called_once()
    assert mock_gen.call_args.args[0] == "java"
    assert "FROM eclipse-temurin" in capsys.readouterr().out


def test_main_prints_clean_error_on_generation_failure(capsys):
    with patch(
        "dockerfile_generator.cli.generate_dockerfile",
        side_effect=DockerfileGenerationError("Ollama is not running"),
    ):
        exit_code = main(["python"])

    assert exit_code == 1
    assert "Error: Ollama is not running" in capsys.readouterr().err


def test_main_passes_flags_through(capsys):
    with patch("dockerfile_generator.cli.generate_dockerfile", return_value="FROM rust:1\n") as mock_gen:
        main(["rust", "--model", "qwen2.5-coder", "--host", "http://example:11434", "--timeout", "30"])

    mock_gen.assert_called_once_with(
        "rust", model="qwen2.5-coder", host="http://example:11434", timeout=30.0
    )
