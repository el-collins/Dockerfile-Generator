"""Command-line interface for dockerfile-generator."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from dockerfile_generator.generator import (
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    DockerfileGenerationError,
    generate_dockerfile,
)

logger = logging.getLogger("dockerfile_generator")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dockerfile-gen",
        description="Generate a Dockerfile for a programming language using a local LLM via Ollama.",
    )
    parser.add_argument(
        "language",
        nargs="?",
        help="Programming language to generate a Dockerfile for. "
        "If omitted, you'll be prompted for it interactively.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("DOCKERFILE_GEN_MODEL", DEFAULT_MODEL),
        help=f"Ollama model to use (default: %(default)s, or $DOCKERFILE_GEN_MODEL)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Ollama host URL (default: $OLLAMA_HOST or http://localhost:11434)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Seconds to wait for Ollama before giving up (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write the Dockerfile to this path instead of printing to stdout",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(message)s",
    )

    try:
        language = args.language if args.language is not None else input("Enter the programming language: ")
        language = language.strip()
        if not language:
            print("Error: language must not be empty.", file=sys.stderr)
            return 1

        dockerfile = generate_dockerfile(
            language,
            model=args.model,
            host=args.host,
            timeout=args.timeout,
        )
    except DockerfileGenerationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130

    if args.output:
        args.output.write_text(dockerfile, encoding="utf-8")
        print(f"Dockerfile written to {args.output}")
    else:
        print(dockerfile)

    return 0


if __name__ == "__main__":
    sys.exit(main())
