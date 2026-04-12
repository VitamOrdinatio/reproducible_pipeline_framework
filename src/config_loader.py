"""
Load and validate pipeline configuration from a YAML file.

This module is intentionally simple for Version 1 of the
reproducible_pipeline_framework repository.

Responsibilities:
- confirm the config file exists
- load YAML into a Python dictionary
- validate that the config is a dictionary
- verify required top-level sections exist
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REQUIRED_TOP_LEVEL_KEYS = [
    "project",
    "run",
    "paths",
    "logging",
    "stages",
    "validation",
    "cleaning",
    "annotation",
    "filtering",
    "outputs",
    "metadata",
]


def load_config(config_path: str | Path) -> dict[str, Any]:
    """
    Load a YAML configuration file and validate its basic structure.

    Parameters
    ----------
    config_path : str | Path
        Path to the YAML config file.

    Returns
    -------
    dict[str, Any]
        Parsed configuration as a Python dictionary.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    ValueError
        If the YAML is empty, malformed, or missing required sections.
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    if not config_file.is_file():
        raise ValueError(f"Config path is not a file: {config_file}")

    try:
        with config_file.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ValueError(f"Failed to parse YAML config: {config_file}") from exc

    if config is None:
        raise ValueError(f"Config file is empty: {config_file}")

    if not isinstance(config, dict):
        raise ValueError(f"Top-level YAML structure must be a dictionary: {config_file}")

    missing_keys = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in config]
    if missing_keys:
        missing_str = ", ".join(missing_keys)
        raise ValueError(f"Config file is missing required top-level sections: {missing_str}")

    return config


def validate_config_paths(config: dict[str, Any]) -> None:
    """
    Perform minimal path validation on required path fields.

    Version 1 keeps this validation intentionally light.
    We validate presence of required keys, not existence of every path,
    because some outputs will be created during pipeline execution.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Raises
    ------
    ValueError
        If required path keys are missing.
    """
    if "paths" not in config or not isinstance(config["paths"], dict):
        raise ValueError("Config must include a 'paths' section as a dictionary.")

    required_path_keys = [
        "input_vcf",
        "example_input_vcf",
        "interim_dir",
        "processed_dir",
        "results_root",
    ]

    missing_path_keys = [key for key in required_path_keys if key not in config["paths"]]
    if missing_path_keys:
        missing_str = ", ".join(missing_path_keys)
        raise ValueError(f"Config 'paths' section is missing required keys: {missing_str}")


def get_input_vcf_path(config: dict[str, Any]) -> str:
    """
    Return the active input VCF path based on the run configuration.

    If use_example_data is true, use paths.example_input_vcf.
    Otherwise, use paths.input_vcf.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    str
        Path to the selected input VCF.

    Raises
    ------
    ValueError
        If the required fields are missing.
    """
    try:
        use_example_data = config["run"]["use_example_data"]
        example_input_vcf = config["paths"]["example_input_vcf"]
        input_vcf = config["paths"]["input_vcf"]
    except KeyError as exc:
        raise ValueError(f"Missing required config field: {exc}") from exc

    return example_input_vcf if use_example_data else input_vcf


if __name__ == "__main__":
    test_path = Path("config/config.yaml")
    try:
        loaded_config = load_config(test_path)
        validate_config_paths(loaded_config)
        selected_input = get_input_vcf_path(loaded_config)
        print("Config loaded successfully.")
        print(f"Selected input VCF: {selected_input}")
    except Exception as exc:
        print(f"Config validation failed: {exc}")