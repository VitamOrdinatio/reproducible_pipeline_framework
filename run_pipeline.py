"""
CLI entry point for the reproducible pipeline framework.

This script:
- accepts a config file path from the command line
- executes the pipeline through src.pipeline_runner
- prints a short terminal summary at the end

Version 1 intentionally keeps this interface simple.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.pipeline_runner import run_pipeline


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Run the reproducible pipeline framework."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to the pipeline YAML configuration file.",
    )
    return parser.parse_args()


def main() -> int:
    """
    Main CLI entry point.

    Returns
    -------
    int
        Exit status code. Zero indicates success.
    """
    args = parse_args()
    config_path = Path(args.config)

    try:
        metadata = run_pipeline(config_path)
    except Exception as exc:
        print(f"Pipeline execution failed: {exc}", file=sys.stderr)
        return 1

    print("Pipeline execution complete.")
    print(f"Run status: {metadata['run_status']}")
    print(f"Run ID: {metadata['run_id']}")
    print(f"Run directory: {metadata['run_dir']}")

    return 0 if metadata["run_status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())