"""
Pipeline orchestration for the reproducible pipeline framework.

This module is responsible for:
- loading and validating configuration
- initializing run-specific paths
- initializing logging
- copying the config snapshot into the run directory
- executing enabled pipeline stages in order
- maintaining a shared state object
- writing run metadata

Version 1 design:
- sequential stage execution
- function-based stages
- fail-fast behavior controlled by config
"""

from __future__ import annotations

import shutil
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config_loader import get_input_vcf_path, load_config, validate_config_paths
from src.logger import setup_logger
from src.path_manager import initialize_run_paths

from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
from pipeline.stage_02_validate_data import run_stage as run_stage_02_validate_data
from pipeline.stage_03_clean_data import run_stage as run_stage_03_clean_data
from pipeline.stage_04_transform_data import run_stage as run_stage_04_transform_data
from pipeline.stage_05_analyze_data import run_stage as run_stage_05_analyze_data
from pipeline.stage_06_write_summary import run_stage as run_stage_06_write_summary


STAGE_REGISTRY = [
    ("load_data", run_stage_01_load_data),
    ("validate_data", run_stage_02_validate_data),
    ("clean_data", run_stage_03_clean_data),
    ("transform_data", run_stage_04_transform_data),
    ("analyze_data", run_stage_05_analyze_data),
    ("write_summary", run_stage_06_write_summary),
]


def copy_config_snapshot(config_path: str | Path, snapshot_path: Path) -> None:
    """
    Copy the original config file into the run directory.

    Parameters
    ----------
    config_path : str | Path
        Original config file path.
    snapshot_path : Path
        Destination path inside the run directory.
    """
    source = Path(config_path)
    shutil.copy2(source, snapshot_path)


def build_initial_metadata(config: dict[str, Any], config_path: str | Path, paths: dict[str, Path]) -> dict[str, Any]:
    """
    Build the initial metadata dictionary for this pipeline run.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    config_path : str | Path
        Original config file path.
    paths : dict[str, Path]
        Run-specific resolved paths.

    Returns
    -------
    dict[str, Any]
        Initial metadata dictionary.
    """
    return {
        "project_name": config["project"]["name"],
        "pipeline_name": config["project"]["pipeline_name"],
        "pipeline_version": config["project"]["version"],
        "run_id": paths["run_id"].name,
        "run_status": "started",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "duration_seconds": None,
        "config_path_original": str(Path(config_path).resolve()),
        "config_path_snapshot": str(paths["config_snapshot_file"]),
        "input_vcf_selected": get_input_vcf_path(config),
        "results_root": str(paths["results_root"]),
        "run_dir": str(paths["run_dir"]),
        "hostname": socket.gethostname(),
        "python_version": sys.version.split()[0],
        "stage_status": {},
    }


def finalize_metadata(metadata: dict[str, Any], run_status: str, start_time_seconds: float) -> dict[str, Any]:
    """
    Finalize metadata at the end of the run.

    Parameters
    ----------
    metadata : dict[str, Any]
        Current metadata dictionary.
    run_status : str
        Final run status, e.g. 'success' or 'failed'.
    start_time_seconds : float
        Unix timestamp recorded at run start.

    Returns
    -------
    dict[str, Any]
        Finalized metadata dictionary.
    """
    metadata["run_status"] = run_status
    metadata["end_time"] = datetime.now().isoformat()
    metadata["duration_seconds"] = round(time.time() - start_time_seconds, 3)
    return metadata


def write_metadata(metadata: dict[str, Any], metadata_path: Path) -> None:
    """
    Write metadata to disk as JSON.

    Parameters
    ----------
    metadata : dict[str, Any]
        Metadata dictionary.
    metadata_path : Path
        Destination JSON file path.
    """
    import json

    with metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)


def run_pipeline(config_path: str | Path) -> dict[str, Any]:
    """
    Execute the pipeline end-to-end.

    Parameters
    ----------
    config_path : str | Path
        Path to the pipeline YAML config file.

    Returns
    -------
    dict[str, Any]
        Final metadata dictionary.

    Raises
    ------
    Exception
        Re-raises stage errors when fail_fast is enabled.
    """
    start_time_seconds = time.time()

    config = load_config(config_path)
    validate_config_paths(config)
    paths = initialize_run_paths(config)
    copy_config_snapshot(config_path, paths["config_snapshot_file"])

    logger = setup_logger(config, paths["log_file"])
    metadata = build_initial_metadata(config, config_path, paths)

    state: dict[str, Any] = {
        "input_vcf_path": get_input_vcf_path(config),
        "stage_outputs": {},
    }

    logger.info("Pipeline run started.")
    logger.info(f"Run ID: {paths['run_id'].name}")
    logger.info(f"Selected input VCF: {state['input_vcf_path']}")

    fail_fast = config["run"]["fail_fast"]

    try:
        for stage_name, stage_function in STAGE_REGISTRY:
            stage_enabled = config["stages"].get(stage_name, False)

            if not stage_enabled:
                logger.info(f"Skipping stage: {stage_name}")
                metadata["stage_status"][stage_name] = "skipped"
                continue

            logger.info(f"Starting stage: {stage_name}")
            stage_start = time.time()

            try:
                state = stage_function(config, paths, logger, state)
                stage_duration = round(time.time() - stage_start, 3)
                metadata["stage_status"][stage_name] = {
                    "status": "success",
                    "duration_seconds": stage_duration,
                }
                logger.info(f"Completed stage: {stage_name} ({stage_duration} seconds)")
            except Exception as exc:
                stage_duration = round(time.time() - stage_start, 3)
                metadata["stage_status"][stage_name] = {
                    "status": "failed",
                    "duration_seconds": stage_duration,
                    "error": str(exc),
                }
                logger.exception(f"Stage failed: {stage_name}")

                if fail_fast:
                    raise

        finalize_metadata(metadata, run_status="success", start_time_seconds=start_time_seconds)
        logger.info("Pipeline run completed successfully.")

    except Exception as exc:
        finalize_metadata(metadata, run_status="failed", start_time_seconds=start_time_seconds)
        logger.exception(f"Pipeline run failed: {exc}")

    write_metadata(metadata, paths["metadata_file"])
    logger.info(f"Metadata written to: {paths['metadata_file']}")
    logger.info("Pipeline run finished.")

    return metadata


if __name__ == "__main__":
    final_metadata = run_pipeline("config/config.yaml")
    print("Pipeline execution complete.")
    print(f"Run status: {final_metadata['run_status']}")
    print(f"Run ID: {final_metadata['run_id']}")