"""TETRA OS command-line interface."""

from __future__ import annotations

import argparse
import subprocess
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tetra",
        description="TETRA OS — self-improving optimization and discovery system",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="TETRA OS 1.0.0 — Copyright (c) Walter Calmels",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["test", "dashboard"],
        default="test",
        help="Run the integration test suite (default) or launch the web dashboard",
    )
    args = parser.parse_args(argv)

    if args.command == "dashboard":
        from tetra_web_dashboard import start_dashboard

        start_dashboard(host="0.0.0.0", port=8080, debug=False)
        return 0

    return subprocess.call([sys.executable, "tetra_first_test.py"])


if __name__ == "__main__":
    sys.exit(main())
