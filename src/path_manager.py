"""
Create and manage pipeline run paths.

This module is responsible for building a run-specific directory
structure for each pipeline execution.

Version 1 responsibilities:
- create a timestamped run directory
- create standard run subdirectories
- return resolved paths in a dictionary
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


def build_run_id(config: dict[str, Any]) -> str:
    """
    Build a timestamped run identifier from config settings.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    str
        Run identifier such as:
        run_2026_04_11_153000
    """
    try:
        run_name_prefix = config["run"]["run_name_prefix"]
        timestamp_format = config["run"]["timestamp_format"]
    except KeyError as exc:
        raise ValueError(f"Missing required run config field: {exc}") from exc

    timestamp = datetime.now().strftime(timestamp_format)
    return f"{run_name_prefix}_{timestamp}"


def create_directory(path: Path) -> None:
    """
    Create a directory if it does not already exist.

    Parameters
    ----------
    path : Path
        Directory path to create.
    """
    path.mkdir(parents=True, exist_ok=True)


def initialize_run_paths(config: dict[str, Any]) -> dict[str, Path]:
    """
    Create the standard run directory structure and return important paths.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    dict[str, Path]
        Dictionary containing resolved run paths.

    Raises
    ------
    ValueError
        If required config fields are missing.
    """
    try:
        results_root = Path(config["paths"]["results_root"])
        interim_dir = Path(config["paths"]["interim_dir"])
        processed_dir = Path(config["paths"]["processed_dir"])
        log_filename = config["logging"]["log_filename"]
        metadata_filename = config["metadata"]["metadata_filename"]
        config_snapshot_filename = config["metadata"]["config_snapshot_filename"]
    except KeyError as exc:
        raise ValueError(f"Missing required path or metadata config field: {exc}") from exc

    run_id = build_run_id(config)
    run_dir = results_root / run_id
    run_logs_dir = run_dir / "logs"
    run_final_dir = run_dir / "final"
    run_reports_dir = run_dir / "reports"
    run_interim_dir = run_dir / "interim"

    create_directory(results_root)
    create_directory(run_dir)
    create_directory(run_logs_dir)
    create_directory(run_final_dir)
    create_directory(run_reports_dir)
    create_directory(run_interim_dir)
    create_directory(interim_dir)
    create_directory(processed_dir)

    paths = {
        "run_id": Path(run_id),
        "results_root": results_root,
        "run_dir": run_dir,
        "run_logs_dir": run_logs_dir,
        "run_final_dir": run_final_dir,
        "run_reports_dir": run_reports_dir,
        "run_interim_dir": run_interim_dir,
        "interim_dir": interim_dir,
        "processed_dir": processed_dir,
        "log_file": run_logs_dir / log_filename,
        "metadata_file": run_dir / metadata_filename,
        "config_snapshot_file": run_dir / config_snapshot_filename,
    }

    return paths


if __name__ == "__main__":
    from src.config_loader import load_config, validate_config_paths

    config = load_config("config/config.yaml")
    validate_config_paths(config)
    run_paths = initialize_run_paths(config)

    print("Run paths created successfully.")
    for key, value in run_paths.items():
        print(f"{key}: {value}")