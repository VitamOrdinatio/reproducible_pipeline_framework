"""
Create and manage pipeline run paths for Version 2.

Version 2 responsibilities:
- create a timestamped run directory
- create standard run subdirectories
- support both full_pipeline and annotation_only modes
- provide canonical artifact paths for the 13-stage v2 pipeline
- return all important paths in a single dictionary
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
        Run identifier such as run_2026_04_13_153000.
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


def get_execution_mode(config: dict[str, Any]) -> str:
    """
    Return the active execution mode from config.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    str
        Active execution mode.
    """
    try:
        return config["mode"]["execution_mode"]
    except KeyError as exc:
        raise ValueError(f"Missing required mode config field: {exc}") from exc


def initialize_run_paths(config: dict[str, Any]) -> dict[str, Path | str]:
    """
    Create the standard v2 run directory structure and return important paths.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    dict[str, Path | str]
        Dictionary containing resolved run paths and metadata strings.

    Raises
    ------
    ValueError
        If required config fields are missing.
    """
    try:
        raw_dir = Path(config["paths"]["raw_dir"])
        interim_dir = Path(config["paths"]["interim_dir"])
        processed_dir = Path(config["paths"]["processed_dir"])
        results_root = Path(config["paths"]["results_root"])

        log_filename = config["logging"]["log_filename"]
        metadata_filename = config["metadata"]["metadata_filename"]
        config_snapshot_filename = config["metadata"]["config_snapshot_filename"]

        outputs = config["outputs"]
        aligned_bam_filename = outputs["aligned_bam_filename"]
        sorted_bam_filename = outputs["sorted_bam_filename"]
        bam_index_filename = outputs["bam_index_filename"]
        raw_vcf_filename = outputs["raw_vcf_filename"]
        normalized_vcf_filename = outputs["normalized_vcf_filename"]
        annotated_vcf_filename = outputs["annotated_vcf_filename"]
        annotated_table_filename = outputs["annotated_table_filename"]
        coding_track_filename = outputs["coding_track_filename"]
        noncoding_track_filename = outputs["noncoding_track_filename"]
        interpreted_coding_filename = outputs["interpreted_coding_filename"]
        interpreted_noncoding_filename = outputs["interpreted_noncoding_filename"]
        prioritized_variants_filename = outputs["prioritized_variants_filename"]
        validation_notes_filename = outputs["validation_notes_filename"]
        summary_report_filename = outputs["summary_report_filename"]
        summary_table_filename = outputs["summary_table_filename"]

    except KeyError as exc:
        raise ValueError(f"Missing required path, output, or metadata config field: {exc}") from exc

    run_id = build_run_id(config)
    execution_mode = get_execution_mode(config)

    run_dir = results_root / run_id
    run_logs_dir = run_dir / "logs"
    run_final_dir = run_dir / "final"
    run_reports_dir = run_dir / "reports"
    run_interim_dir = run_dir / "interim"
    run_validation_dir = run_dir / "validation"

    create_directory(raw_dir)
    create_directory(interim_dir)
    create_directory(processed_dir)
    create_directory(results_root)
    create_directory(run_dir)
    create_directory(run_logs_dir)
    create_directory(run_final_dir)
    create_directory(run_reports_dir)
    create_directory(run_interim_dir)
    create_directory(run_validation_dir)

    paths: dict[str, Path | str] = {
        "run_id": run_id,
        "execution_mode": execution_mode,

        "raw_dir": raw_dir,
        "interim_dir": interim_dir,
        "processed_dir": processed_dir,
        "results_root": results_root,

        "run_dir": run_dir,
        "run_logs_dir": run_logs_dir,
        "run_final_dir": run_final_dir,
        "run_reports_dir": run_reports_dir,
        "run_interim_dir": run_interim_dir,
        "run_validation_dir": run_validation_dir,

        "log_file": run_logs_dir / log_filename,
        "metadata_file": run_dir / metadata_filename,
        "config_snapshot_file": run_dir / config_snapshot_filename,

        # Stage-oriented artifacts
        "aligned_bam": interim_dir / aligned_bam_filename,
        "sorted_bam": interim_dir / sorted_bam_filename,
        "bam_index": interim_dir / bam_index_filename,
        "raw_vcf": interim_dir / raw_vcf_filename,
        "normalized_vcf": interim_dir / normalized_vcf_filename,

        "annotated_vcf": processed_dir / annotated_vcf_filename,
        "annotated_table": processed_dir / annotated_table_filename,

        "coding_track_table": run_final_dir / coding_track_filename,
        "noncoding_track_table": run_final_dir / noncoding_track_filename,
        "interpreted_coding_table": run_final_dir / interpreted_coding_filename,
        "interpreted_noncoding_table": run_final_dir / interpreted_noncoding_filename,
        "prioritized_table": run_final_dir / prioritized_variants_filename,

        "validation_notes": run_validation_dir / validation_notes_filename,

        "summary_report": run_reports_dir / summary_report_filename,
        "summary_table": run_reports_dir / summary_table_filename,
    }

    return paths


if __name__ == "__main__":
    from src.config_loader import load_config, validate_config

    config = load_config("config/config.yaml")
    validate_config(config)
    run_paths = initialize_run_paths(config)

    print("Run paths created successfully.")
    for key, value in run_paths.items():
        print(f"{key}: {value}")