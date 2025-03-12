"""Enables `python -m dockerfile_generator`."""

import sys

from dockerfile_generator.cli import main

if __name__ == "__main__":
    sys.exit(main())
