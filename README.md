# Dockerfile Generator (Local LLM)

Generates a Dockerfile for whatever programming language you give it, using a
local LLM through [Ollama](https://ollama.com) — no cloud API key, no
per-token cost.

## Prerequisites

- [Ollama](https://ollama.com) installed and running
- The model pulled locally:

  ```
  ollama pull llama3.2
  ```

- Python 3.9+

## Install

```
python -m venv venv
venv\Scripts\activate      # Windows
pip install -e ".[dev]"    # editable install + test dependencies
```

Use `pip install -e .` instead if you don't need the test suite.

## Usage

```
dockerfile-gen java
dockerfile-gen node.js -o Dockerfile
dockerfile-gen                          # no language given -> prompts interactively
dockerfile-gen rust --model qwen2.5-coder --timeout 60
```

Equivalently, without installing the console script: `python -m dockerfile_generator <args>`.

### Flags

| Flag | Default | Description |
| --- | --- | --- |
| `language` (positional) | — | Programming language to generate a Dockerfile for. If omitted, you're prompted for it. |
| `--model` | `llama3.2` (or `$DOCKERFILE_GEN_MODEL`) | Ollama model to use. |
| `--host` | `$OLLAMA_HOST` / `http://localhost:11434` | Ollama server URL. |
| `--timeout` | `120` | Seconds to wait for a response before giving up. |
| `-o, --output` | — | Write the Dockerfile to this path instead of printing to stdout. |
| `-v, --verbose` | off | Enable debug logging. |

### Errors

Ollama not running, the model not pulled yet, or a request timing out all
produce a one-line `Error: ...` message on stderr and exit code `1` — not a
Python traceback.

## Testing

```
pytest
```

The test suite mocks the Ollama client, so it runs without Ollama installed
or running.

## Project layout

```
src/dockerfile_generator/
├── generator.py   # prompt building, the Ollama call, output cleanup, error mapping
└── cli.py         # argparse-based command-line interface
tests/             # pytest suite (fully mocked)
```
