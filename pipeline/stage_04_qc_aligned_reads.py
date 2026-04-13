"""
Stage 04: Perform QC on aligned reads.

Version 2 responsibilities:
- operate in full_pipeline mode
- validate sorted BAM and BAM index artifacts from Stage 03
- generate lightweight QC summaries
- optionally write a mock QC report artifact
- update QC fields and stage_outputs in state

This stage does not perform real samtools QC inside the framework repo.
Instead, it records lightweight, reproducible QC summaries based on the
mock BAM artifacts created upstream.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def validate_bam_artifacts(state: dict[str, Any]) -> tuple[Path, Path]:
    """
    Validate required BAM-related artifacts from Stage 03.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    tuple[Path, Path]
        Sorted BAM path and BAM index path.

    Raises
    ------
    ValueError
        If required artifact paths are missing.
    FileNotFoundError
        If required artifact files do not exist.
    """
    sorted_bam = state["artifacts"].get("sorted_bam")
    bam_index = state["artifacts"].get("bam_index")

    if not sorted_bam:
        raise ValueError("Stage 04 requires artifacts.sorted_bam.")
    if not bam_index:
        raise ValueError("Stage 04 requires artifacts.bam_index.")

    sorted_bam_path = Path(sorted_bam)
    bam_index_path = Path(bam_index)

    if not sorted_bam_path.exists():
        raise FileNotFoundError(f"Sorted BAM not found: {sorted_bam_path}")
    if not bam_index_path.exists():
        raise FileNotFoundError(f"BAM index not found: {bam_index_path}")

    return sorted_bam_path, bam_index_path


def write_mock_qc_report(
    output_path: Path,
    sample_id: str,
    sorted_bam_path: Path,
    bam_index_path: Path,
    total_reads: int,
    mapped_reads: int,
    mapping_rate: float,
) -> None:
    """
    Write a mock aligned-read QC report.

    Parameters
    ----------
    output_path : Path
        Destination QC report path.
    sample_id : str
        Sample identifier.
    sorted_bam_path : Path
        Sorted BAM path.
    bam_index_path : Path
        BAM index path.
    total_reads : int
        Total reads estimate.
    mapped_reads : int
        Mapped reads estimate.
    mapping_rate : float
        Mapping rate estimate.
    """
    content = [
        "MOCK_ALIGNMENT_QC_REPORT",
        f"sample_id={sample_id}",
        f"sorted_bam={sorted_bam_path}",
        f"bam_index={bam_index_path}",
        f"total_reads={total_reads}",
        f"mapped_reads={mapped_reads}",
        f"mapping_rate={mapping_rate}",
        "qc_tools=samtools_flagstat_placeholder,samtools_stats_placeholder,samtools_idxstats_placeholder",
        "status=qc_mock_output",
    ]

    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(content) + "\n")


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 04: QC aligned reads.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    paths : dict[str, Path | str]
        Resolved pipeline paths.
    logger : logging.Logger
        Configured pipeline logger.
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    dict[str, Any]
        Updated state.

    Raises
    ------
    ValueError
        If execution mode is incorrect or required state keys are missing.
    """
    logger.info("Stage 04: QC aligned reads.")

    execution_mode = state["run"]["mode"]
    if execution_mode != "full_pipeline":
        raise ValueError("Stage 04 should only run in full_pipeline mode.")

    sorted_bam_path, bam_index_path = validate_bam_artifacts(state)

    sample_id = state["sample"]["sample_id"]

    alignment_qc_prior = state["qc"].get("alignment_qc", {})
    read_count_r1 = int(alignment_qc_prior.get("read_count_r1", 0))
    read_count_r2 = int(alignment_qc_prior.get("read_count_r2", 0))

    total_reads = read_count_r1 + read_count_r2
    mapped_reads = total_reads
    mapping_rate = 1.0 if total_reads > 0 else 0.0

    qc_report_path = Path(paths["run_reports_dir"]) / "aligned_read_qc_report.txt"
    write_mock_qc_report(
        output_path=qc_report_path,
        sample_id=sample_id,
        sorted_bam_path=sorted_bam_path,
        bam_index_path=bam_index_path,
        total_reads=total_reads,
        mapped_reads=mapped_reads,
        mapping_rate=mapping_rate,
    )

    state["qc"]["alignment_qc"] = {
        **alignment_qc_prior,
        "qc_completed": True,
        "mock_qc": True,
        "sorted_bam_present": True,
        "bam_index_present": True,
        "total_reads": total_reads,
        "mapped_reads": mapped_reads,
        "mapping_rate": mapping_rate,
        "qc_report": str(qc_report_path),
    }

    state["stage_outputs"]["stage_04_qc_aligned_reads"] = {
        "status": "success",
        "sorted_bam": str(sorted_bam_path),
        "bam_index": str(bam_index_path),
        "total_reads": total_reads,
        "mapped_reads": mapped_reads,
        "mapping_rate": mapping_rate,
        "qc_report": str(qc_report_path),
    }

    logger.info(f"Mock aligned-read QC report written to: {qc_report_path}")

    return state


if __name__ == "__main__":
    import logging

    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
    from pipeline.stage_02_align_data import run_stage as run_stage_02_align_data
    from pipeline.stage_03_process_bam import run_stage as run_stage_03_process_bam
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_04_test")

    test_config = load_config("config/config.yaml")
    validate_config(test_config)
    test_paths = initialize_run_paths(test_config)
    test_state = initialize_state(test_config, "config/config.yaml", test_paths)

    test_state = run_stage_01_load_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_02_align_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_03_process_bam(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 04 completed successfully.")
    print(test_state["stage_outputs"]["stage_04_qc_aligned_reads"])