"""
Centralized logging setup for the pipeline.

This module creates a configured logger that writes to:
- a run-specific log file
- optionally the console

Version 1 design:
- single logger per run
- simple, readable formatting
- no overengineering (no multiple handlers per stage)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any


def setup_logger(config: dict[str, Any], log_file: Path) -> logging.Logger:
    """
    Create and configure the pipeline logger.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    log_file : Path
        Path to the log file for this run.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """
    try:
        log_level_str = config["logging"]["level"]
        log_to_console = config["logging"]["log_to_console"]
    except KeyError as exc:
        raise ValueError(f"Missing logging config field: {exc}") from exc

    # Convert string log level to logging constant
    log_level = getattr(logging, log_level_str.upper(), None)
    if log_level is None:
        raise ValueError(f"Invalid log level: {log_level_str}")

    # Create logger
    logger = logging.getLogger("pipeline_logger")
    logger.setLevel(log_level)

    # Prevent duplicate handlers if logger is reused
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (optional)
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.info("Logger initialized.")
    logger.info(f"Log file: {log_file}")

    return logger


if __name__ == "__main__":
    from src.config_loader import load_config, validate_config_paths
    from src.path_manager import initialize_run_paths

    config = load_config("config/config.yaml")
    validate_config_paths(config)
    paths = initialize_run_paths(config)

    logger = setup_logger(config, paths["log_file"])

    logger.info("Test log entry.")