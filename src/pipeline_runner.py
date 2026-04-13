"""
Pipeline orchestration for Version 2 of the reproducible pipeline framework.

Version 2 responsibilities:
- load and validate v2 configuration
- initialize run-specific paths
- initialize logging
- copy the config snapshot into the run directory
- initialize the nested v2 state object
- execute enabled pipeline stages in order
- support both full_pipeline and annotation_only modes
- write final metadata

This version keeps stage execution explicit and sequential.
"""

from __future__ import annotations

import json
import shutil
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config_loader import get_active_inputs, get_execution_mode, load_config, validate_config
from src.logger import setup_logger
from src.path_manager import initialize_run_paths

from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
from pipeline.stage_02_align_data import run_stage as run_stage_02_align_data
from pipeline.stage_03_process_bam import run_stage as run_stage_03_process_bam
from pipeline.stage_04_qc_aligned_reads import run_stage as run_stage_04_qc_aligned_reads
from pipeline.stage_05_call_variants import run_stage as run_stage_05_call_variants
from pipeline.stage_06_normalize_vcf import run_stage as run_stage_06_normalize_vcf
from pipeline.stage_07_annotate_variants import run_stage as run_stage_07_annotate_variants
from pipeline.stage_08_filter_and_partition import run_stage as run_stage_08_filter_and_partition
from pipeline.stage_09_interpret_coding import run_stage as run_stage_09_interpret_coding
from pipeline.stage_10_interpret_noncoding import run_stage as run_stage_10_interpret_noncoding
from pipeline.stage_11_prioritize_variants import run_stage as run_stage_11_prioritize_variants
from pipeline.stage_12_validate_variants import run_stage as run_stage_12_validate_variants
from pipeline.stage_13_write_summary import run_stage as run_stage_13_write_summary


STAGE_REGISTRY = [
    ("stage_01_load_data", run_stage_01_load_data),
    ("stage_02_align_data", run_stage_02_align_data),
    ("stage_03_process_bam", run_stage_03_process_bam),
    ("stage_04_qc_aligned_reads", run_stage_04_qc_aligned_reads),
    ("stage_05_call_variants", run_stage_05_call_variants),
    ("stage_06_normalize_vcf", run_stage_06_normalize_vcf),
    ("stage_07_annotate_variants", run_stage_07_annotate_variants),
    ("stage_08_filter_and_partition", run_stage_08_filter_and_partition),
    ("stage_09_interpret_coding", run_stage_09_interpret_coding),
    ("stage_10_interpret_noncoding", run_stage_10_interpret_noncoding),
    ("stage_11_prioritize_variants", run_stage_11_prioritize_variants),
    ("stage_12_validate_variants", run_stage_12_validate_variants),
    ("stage_13_write_summary", run_stage_13_write_summary),
]


MODE_STAGE_GATING = {
    "full_pipeline": {
        "stage_01_load_data": True,
        "stage_02_align_data": True,
        "stage_03_process_bam": True,
        "stage_04_qc_aligned_reads": True,
        "stage_05_call_variants": True,
        "stage_06_normalize_vcf": True,
        "stage_07_annotate_variants": True,
        "stage_08_filter_and_partition": True,
        "stage_09_interpret_coding": True,
        "stage_10_interpret_noncoding": True,
        "stage_11_prioritize_variants": True,
        "stage_12_validate_variants": True,
        "stage_13_write_summary": True,
    },
    "annotation_only": {
        "stage_01_load_data": True,
        "stage_02_align_data": False,
        "stage_03_process_bam": False,
        "stage_04_qc_aligned_reads": False,
        "stage_05_call_variants": False,
        "stage_06_normalize_vcf": True,
        "stage_07_annotate_variants": True,
        "stage_08_filter_and_partition": True,
        "stage_09_interpret_coding": True,
        "stage_10_interpret_noncoding": True,
        "stage_11_prioritize_variants": True,
        "stage_12_validate_variants": True,
        "stage_13_write_summary": True,
    },
}


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
    shutil.copy2(Path(config_path), snapshot_path)


def initialize_state(
    config: dict[str, Any],
    config_path: str | Path,
    paths: dict[str, Path | str],
) -> dict[str, Any]:
    """
    Initialize the canonical v2 nested state object.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    config_path : str | Path
        Original config path.
    paths : dict[str, Path | str]
        Resolved run paths.

    Returns
    -------
    dict[str, Any]
        Initialized nested state object.
    """
    active_inputs = get_active_inputs(config)
    execution_mode = get_execution_mode(config)

    state: dict[str, Any] = {
        "run": {
            "run_id": str(paths["run_id"]),
            "mode": execution_mode,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "pipeline_version": config["project"]["version"],
            "config_path": str(Path(config_path).resolve()),
            "log_file": str(paths["log_file"]),
            "metadata_file": str(paths["metadata_file"]),
        },
        "sample": {
            "sample_id": config["sample"]["sample_id"],
            "cohort_id": config["sample"]["cohort_id"],
            "assay_type": config["sample"]["assay_type"],
            "reference_genome": config["sample"]["reference_genome"],
        },
        "inputs": {
            "fastq_1": active_inputs["fastq_1"],
            "fastq_2": active_inputs["fastq_2"],
            "input_vcf": active_inputs["input_vcf"],
            "mode_confirmed": execution_mode,
        },
        "artifacts": {
            "aligned_bam": None,
            "sorted_bam": None,
            "bam_index": None,
            "raw_vcf": None,
            "normalized_vcf": None,
            "annotated_vcf": None,
            "annotated_table": None,
            "coding_track_table": None,
            "noncoding_track_table": None,
            "interpreted_coding_table": None,
            "interpreted_noncoding_table": None,
            "prioritized_table": None,
            "validation_notes": None,
            "summary_report": None,
        },
        "qc": {
            "input_qc": {},
            "alignment_qc": {},
            "bam_processing_qc": {},
            "variant_calling_qc": {},
            "annotation_qc": {},
            "filtering_qc": {},
            "validation_qc": {},
        },
        "annotations": {
            "resources_used": [],
            "annotation_fields_present": [],
            "annotation_completeness": {},
            "ai_annotations_used": [],
        },
        "tracks": {
            "coding": {},
            "noncoding": {},
        },
        "reports": {},
        "stage_outputs": {},
        "warnings": [],
        "errors": [],
    }

    return state


def build_initial_metadata(
    config: dict[str, Any],
    config_path: str | Path,
    paths: dict[str, Path | str],
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Build initial metadata for this pipeline run.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    config_path : str | Path
        Original config path.
    paths : dict[str, Path | str]
        Resolved run paths.
    state : dict[str, Any]
        Initialized pipeline state.

    Returns
    -------
    dict[str, Any]
        Initial metadata dictionary.
    """
    return {
        "project_name": config["project"]["name"],
        "pipeline_name": config["project"]["pipeline_name"],
        "pipeline_version": config["project"]["version"],
        "run_id": str(paths["run_id"]),
        "execution_mode": state["run"]["mode"],
        "run_status": "started",
        "start_time": state["run"]["start_time"],
        "end_time": None,
        "duration_seconds": None,
        "config_path_original": str(Path(config_path).resolve()),
        "config_path_snapshot": str(paths["config_snapshot_file"]),
        "results_root": str(paths["results_root"]),
        "run_dir": str(paths["run_dir"]),
        "sample_id": state["sample"]["sample_id"],
        "hostname": socket.gethostname(),
        "python_version": sys.version.split()[0],
        "stage_status": {},
        "warnings": [],
        "errors": [],
    }


def finalize_metadata(metadata: dict[str, Any], state: dict[str, Any], start_time_seconds: float) -> dict[str, Any]:
    """
    Finalize metadata at the end of the run.

    Parameters
    ----------
    metadata : dict[str, Any]
        Current metadata dictionary.
    state : dict[str, Any]
        Final pipeline state.
    start_time_seconds : float
        Unix timestamp recorded at run start.

    Returns
    -------
    dict[str, Any]
        Finalized metadata dictionary.
    """
    metadata["run_status"] = state["run"]["status"]
    metadata["end_time"] = datetime.now().isoformat()
    metadata["duration_seconds"] = round(time.time() - start_time_seconds, 3)
    metadata["warnings"] = list(state["warnings"])
    metadata["errors"] = list(state["errors"])
    return metadata


def write_metadata(metadata: dict[str, Any], metadata_path: Path) -> None:
    """
    Write metadata to disk as JSON.

    Parameters
    ----------
    metadata : dict[str, Any]
        Metadata dictionary.
    metadata_path : Path
        Destination metadata file.
    """
    with metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)


def should_run_stage(config: dict[str, Any], execution_mode: str, stage_name: str) -> bool:
    """
    Determine whether a stage should run based on config and execution mode.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    execution_mode : str
        Active execution mode.
    stage_name : str
        Canonical stage name.

    Returns
    -------
    bool
        True if the stage should run.
    """
    stage_toggle = config["stages"].get(stage_name, False)
    mode_gate = MODE_STAGE_GATING[execution_mode].get(stage_name, False)
    return bool(stage_toggle and mode_gate)


def run_pipeline(config_path: str | Path) -> dict[str, Any]:
    """
    Execute the v2 pipeline end-to-end.

    Parameters
    ----------
    config_path : str | Path
        Path to the pipeline YAML config file.

    Returns
    -------
    dict[str, Any]
        Final metadata dictionary.
    """
    start_time_seconds = time.time()

    config = load_config(config_path)
    validate_config(config)
    paths = initialize_run_paths(config)
    copy_config_snapshot(config_path, Path(paths["config_snapshot_file"]))

    logger = setup_logger(config, Path(paths["log_file"]))
    state = initialize_state(config, config_path, paths)
    metadata = build_initial_metadata(config, config_path, paths, state)

    execution_mode = state["run"]["mode"]
    fail_fast = config["run"]["fail_fast"]

    logger.info("Pipeline run started.")
    logger.info(f"Run ID: {state['run']['run_id']}")
    logger.info(f"Execution mode: {execution_mode}")
    logger.info(f"Sample ID: {state['sample']['sample_id']}")

    try:
        for stage_name, stage_function in STAGE_REGISTRY:
            if not should_run_stage(config, execution_mode, stage_name):
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
                state["errors"].append({
                    "stage": stage_name,
                    "message": str(exc),
                })
                metadata["stage_status"][stage_name] = {
                    "status": "failed",
                    "duration_seconds": stage_duration,
                    "error": str(exc),
                }
                logger.exception(f"Stage failed: {stage_name}")

                state["run"]["status"] = "failed"

                if fail_fast:
                    raise

        if state["run"]["status"] != "failed":
            state["run"]["status"] = "success"

    except Exception as exc:
        logger.exception(f"Pipeline run failed: {exc}")
        state["run"]["status"] = "failed"

    state["run"]["end_time"] = datetime.now().isoformat()

    metadata = finalize_metadata(metadata, state, start_time_seconds)
    write_metadata(metadata, Path(paths["metadata_file"]))

    logger.info(f"Metadata written to: {paths['metadata_file']}")
    logger.info("Pipeline run finished.")

    return metadata


if __name__ == "__main__":
    final_metadata = run_pipeline("config/config.yaml")
    print("Pipeline execution complete.")
    print(f"Run status: {final_metadata['run_status']}")
    print(f"Run ID: {final_metadata['run_id']}")
    print(f"Execution mode: {final_metadata['execution_mode']}")
    print(f"Run directory: {final_metadata['run_dir']}")