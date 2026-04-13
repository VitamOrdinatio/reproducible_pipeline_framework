"""
Stage 01: Load input data for Version 2.

Version 2 responsibilities:
- validate execution mode
- validate required input file paths for the active mode
- initialize input-related state summaries
- record basic input QC
- avoid heavy parsing at this stage

This stage supports:
- full_pipeline mode (FASTQ input)
- annotation_only mode (VCF input)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def validate_file_exists(path_str: str | None, label: str) -> dict[str, Any]:
    """
    Validate that a required file exists.

    Parameters
    ----------
    path_str : str | None
        File path as a string.
    label : str
        Human-readable label for error messages and summaries.

    Returns
    -------
    dict[str, Any]
        Summary dictionary describing the file check.

    Raises
    ------
    ValueError
        If the path is missing.
    FileNotFoundError
        If the file does not exist.
    """
    if not path_str:
        raise ValueError(f"Missing required input path for: {label}")

    path = Path(path_str)

    if not path.exists():
        raise FileNotFoundError(f"Required input file not found for {label}: {path}")

    if not path.is_file():
        raise ValueError(f"Input path is not a file for {label}: {path}")

    return {
        "label": label,
        "path": str(path),
        "exists": True,
        "size_bytes": path.stat().st_size,
    }


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 01: load input data context.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    paths : dict[str, Path | str]
        Resolved run paths.
    logger : logging.Logger
        Configured pipeline logger.
    state : dict[str, Any]
        Shared nested v2 pipeline state.

    Returns
    -------
    dict[str, Any]
        Updated state.

    Raises
    ------
    ValueError
        If required state keys are missing or mode is invalid.
    FileNotFoundError
        If required input files do not exist.
    """
    logger.info("Stage 01: loading input data context.")

    if "run" not in state or "inputs" not in state or "qc" not in state:
        raise ValueError("Stage 01 requires state sections: 'run', 'inputs', and 'qc'.")

    execution_mode = state["run"]["mode"]
    input_qc: dict[str, Any] = {
        "mode": execution_mode,
        "files_checked": [],
    }

    if execution_mode == "full_pipeline":
        logger.info("Stage 01 operating in full_pipeline mode.")

        fastq_1_summary = validate_file_exists(state["inputs"].get("fastq_1"), "FASTQ R1")
        fastq_2_summary = validate_file_exists(state["inputs"].get("fastq_2"), "FASTQ R2")

        input_qc["files_checked"].append(fastq_1_summary)
        input_qc["files_checked"].append(fastq_2_summary)
        input_qc["files_found"] = True

        logger.info(f"Validated FASTQ R1: {fastq_1_summary['path']}")
        logger.info(f"Validated FASTQ R2: {fastq_2_summary['path']}")

    elif execution_mode == "annotation_only":
        logger.info("Stage 01 operating in annotation_only mode.")

        vcf_summary = validate_file_exists(state["inputs"].get("input_vcf"), "input VCF")
        input_qc["files_checked"].append(vcf_summary)
        input_qc["files_found"] = True

        logger.info(f"Validated input VCF: {vcf_summary['path']}")

    else:
        raise ValueError(f"Unsupported execution mode encountered in Stage 01: {execution_mode}")

    state["qc"]["input_qc"] = input_qc
    state["stage_outputs"]["stage_01_load_data"] = {
        "status": "success",
        "mode": execution_mode,
        "files_checked": input_qc["files_checked"],
    }

    return state


if __name__ == "__main__":
    import logging

    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_01_test")

    test_config = load_config("config/config.yaml")
    validate_config(test_config)
    test_paths = initialize_run_paths(test_config)
    test_state = initialize_state(test_config, "config/config.yaml", test_paths)

    updated_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 01 completed successfully.")
    print(updated_state["stage_outputs"]["stage_01_load_data"])