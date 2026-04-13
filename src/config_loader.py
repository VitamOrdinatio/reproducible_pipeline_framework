"""
Load and validate pipeline configuration from a YAML file.

Version 2 responsibilities:
- confirm the config file exists
- load YAML into a Python dictionary
- validate required top-level sections
- validate execution mode
- validate mode-specific required input paths
- expose helper functions for selecting active inputs
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REQUIRED_TOP_LEVEL_KEYS = [
    "project",
    "run",
    "mode",
    "sample",
    "paths",
    "references",
    "resources",
    "tools",
    "logging",
    "stages",
    "validation",
    "alignment",
    "bam_processing",
    "variant_calling",
    "vcf_normalization",
    "annotation",
    "filtering",
    "interpretation",
    "prioritization",
    "validation_step",
    "outputs",
    "metadata",
]

SUPPORTED_EXECUTION_MODES = {
    "full_pipeline",
    "annotation_only",
}


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


def validate_execution_mode(config: dict[str, Any]) -> str:
    """
    Validate and return the active execution mode.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    str
        Active execution mode.

    Raises
    ------
    ValueError
        If the execution mode is missing or unsupported.
    """
    try:
        execution_mode = config["mode"]["execution_mode"]
    except KeyError as exc:
        raise ValueError(f"Missing required mode config field: {exc}") from exc

    if execution_mode not in SUPPORTED_EXECUTION_MODES:
        supported = ", ".join(sorted(SUPPORTED_EXECUTION_MODES))
        raise ValueError(f"Unsupported execution mode: {execution_mode}. Supported modes: {supported}")

    return execution_mode


def validate_config_paths(config: dict[str, Any]) -> None:
    """
    Perform v2 path validation.

    This validation checks for the presence of required keys rather than the
    existence of all files, because many outputs will be created during execution.

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
        "fastq_1",
        "fastq_2",
        "input_vcf",
        "raw_dir",
        "interim_dir",
        "processed_dir",
        "results_root",
    ]

    missing_path_keys = [key for key in required_path_keys if key not in config["paths"]]
    if missing_path_keys:
        missing_str = ", ".join(missing_path_keys)
        raise ValueError(f"Config 'paths' section is missing required keys: {missing_str}")


def validate_mode_inputs(config: dict[str, Any]) -> None:
    """
    Validate that required inputs are available for the active execution mode.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Raises
    ------
    ValueError
        If required mode-specific inputs are missing.
    """
    execution_mode = validate_execution_mode(config)
    paths = config["paths"]

    if execution_mode == "full_pipeline":
        fastq_1 = paths.get("fastq_1")
        fastq_2 = paths.get("fastq_2")
        if not fastq_1 or not fastq_2:
            raise ValueError("full_pipeline mode requires both paths.fastq_1 and paths.fastq_2.")

    if execution_mode == "annotation_only":
        input_vcf = paths.get("input_vcf")
        if not input_vcf:
            raise ValueError("annotation_only mode requires paths.input_vcf.")


def validate_stage_schema(config: dict[str, Any]) -> None:
    """
    Validate that the v2 stage toggles are present.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Raises
    ------
    ValueError
        If required stage toggles are missing.
    """
    required_stage_keys = [
        "stage_01_load_data",
        "stage_02_align_data",
        "stage_03_process_bam",
        "stage_04_qc_aligned_reads",
        "stage_05_call_variants",
        "stage_06_normalize_vcf",
        "stage_07_annotate_variants",
        "stage_08_filter_and_partition",
        "stage_09_interpret_coding",
        "stage_10_interpret_noncoding",
        "stage_11_prioritize_variants",
        "stage_12_validate_variants",
        "stage_13_write_summary",
    ]

    if "stages" not in config or not isinstance(config["stages"], dict):
        raise ValueError("Config must include a 'stages' section as a dictionary.")

    missing_stage_keys = [key for key in required_stage_keys if key not in config["stages"]]
    if missing_stage_keys:
        missing_str = ", ".join(missing_stage_keys)
        raise ValueError(f"Config 'stages' section is missing required keys: {missing_str}")


def validate_config(config: dict[str, Any]) -> None:
    """
    Run all v2 configuration validation checks.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Raises
    ------
    ValueError
        If validation fails.
    """
    validate_execution_mode(config)
    validate_config_paths(config)
    validate_mode_inputs(config)
    validate_stage_schema(config)


def get_execution_mode(config: dict[str, Any]) -> str:
    """
    Return the active execution mode.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    str
        Active execution mode.
    """
    return validate_execution_mode(config)


def get_active_inputs(config: dict[str, Any]) -> dict[str, str | None]:
    """
    Return the active input set for the selected execution mode.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    dict[str, str | None]
        Active input mapping.

    Raises
    ------
    ValueError
        If required config fields are missing.
    """
    execution_mode = get_execution_mode(config)

    try:
        fastq_1 = config["paths"]["fastq_1"]
        fastq_2 = config["paths"]["fastq_2"]
        input_vcf = config["paths"]["input_vcf"]
    except KeyError as exc:
        raise ValueError(f"Missing required config field: {exc}") from exc

    if execution_mode == "full_pipeline":
        return {
            "mode": execution_mode,
            "fastq_1": fastq_1,
            "fastq_2": fastq_2,
            "input_vcf": None,
        }

    return {
        "mode": execution_mode,
        "fastq_1": None,
        "fastq_2": None,
        "input_vcf": input_vcf,
    }


if __name__ == "__main__":
    test_path = Path("config/config.yaml")

    try:
        loaded_config = load_config(test_path)
        validate_config(loaded_config)
        active_inputs = get_active_inputs(loaded_config)

        print("Config loaded successfully.")
        print(f"Execution mode: {active_inputs['mode']}")
        print(f"FASTQ 1: {active_inputs['fastq_1']}")
        print(f"FASTQ 2: {active_inputs['fastq_2']}")
        print(f"Input VCF: {active_inputs['input_vcf']}")
    except Exception as exc:
        print(f"Config validation failed: {exc}")