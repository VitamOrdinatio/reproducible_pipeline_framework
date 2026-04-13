"""
Stage 03: Process aligned BAM.

Version 2 responsibilities:
- operate in full_pipeline mode
- validate the aligned BAM artifact from Stage 02
- create mock sorted BAM and BAM index artifacts
- record BAM-processing QC summaries
- update artifacts and stage_outputs in state

This stage does not perform real samtools processing inside the framework repo.
Instead, it creates lightweight placeholder artifacts that preserve:
- stage boundaries
- artifact creation
- state transitions
- logging and reproducibility
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def validate_aligned_bam(state: dict[str, Any]) -> Path:
    """
    Validate the aligned BAM artifact from Stage 02.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    Path
        Path to the aligned BAM artifact.

    Raises
    ------
    ValueError
        If the aligned BAM path is missing.
    FileNotFoundError
        If the aligned BAM file does not exist.
    """
    aligned_bam = state["artifacts"].get("aligned_bam")
    if not aligned_bam:
        raise ValueError("Stage 03 requires artifacts.aligned_bam.")

    aligned_bam_path = Path(aligned_bam)
    if not aligned_bam_path.exists():
        raise FileNotFoundError(f"Aligned BAM not found: {aligned_bam_path}")
    if not aligned_bam_path.is_file():
        raise ValueError(f"Aligned BAM path is not a file: {aligned_bam_path}")

    return aligned_bam_path


def write_mock_sorted_bam(
    output_path: Path,
    sample_id: str,
    aligned_bam_path: Path,
    reference_genome: str,
) -> None:
    """
    Write a mock sorted BAM placeholder artifact.

    Parameters
    ----------
    output_path : Path
        Destination sorted BAM path.
    sample_id : str
        Sample identifier.
    aligned_bam_path : Path
        Input aligned BAM path.
    reference_genome : str
        Reference genome label.
    """
    content = [
        "MOCK_SORTED_BAM_PLACEHOLDER",
        f"sample_id={sample_id}",
        f"reference_genome={reference_genome}",
        f"source_aligned_bam={aligned_bam_path}",
        "bam_processing_tool=samtools_placeholder",
        "status=sorted_mock_output",
    ]

    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(content) + "\n")


def write_mock_bam_index(output_path: Path, sorted_bam_path: Path) -> None:
    """
    Write a mock BAM index placeholder artifact.

    Parameters
    ----------
    output_path : Path
        Destination BAM index path.
    sorted_bam_path : Path
        Path to the sorted BAM artifact.
    """
    content = [
        "MOCK_BAI_PLACEHOLDER",
        f"source_sorted_bam={sorted_bam_path}",
        "status=index_mock_output",
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
    Execute Stage 03: process aligned BAM.

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
    logger.info("Stage 03: processing aligned BAM.")

    execution_mode = state["run"]["mode"]
    if execution_mode != "full_pipeline":
        raise ValueError("Stage 03 should only run in full_pipeline mode.")

    aligned_bam_path = validate_aligned_bam(state)

    sample_id = state["sample"]["sample_id"]
    reference_genome = state["sample"]["reference_genome"]

    sorted_bam_path = Path(paths["sorted_bam"])
    bam_index_path = Path(paths["bam_index"])

    if not config["bam_processing"]["create_mock_sorted_bam"]:
        raise ValueError("Stage 03 currently requires bam_processing.create_mock_sorted_bam=true.")
    if not config["bam_processing"]["create_mock_bam_index"]:
        raise ValueError("Stage 03 currently requires bam_processing.create_mock_bam_index=true.")

    write_mock_sorted_bam(
        output_path=sorted_bam_path,
        sample_id=sample_id,
        aligned_bam_path=aligned_bam_path,
        reference_genome=reference_genome,
    )
    write_mock_bam_index(
        output_path=bam_index_path,
        sorted_bam_path=sorted_bam_path,
    )

    sorted_bam_size = sorted_bam_path.stat().st_size
    bam_index_size = bam_index_path.stat().st_size

    state["artifacts"]["sorted_bam"] = str(sorted_bam_path)
    state["artifacts"]["bam_index"] = str(bam_index_path)
    state["qc"]["bam_processing_qc"] = {
        "bam_processing_completed": True,
        "mock_bam_processing": True,
        "sorted_bam_created": True,
        "bam_index_created": True,
        "sorted_bam_size_bytes": sorted_bam_size,
        "bam_index_size_bytes": bam_index_size,
    }
    state["stage_outputs"]["stage_03_process_bam"] = {
        "status": "success",
        "source_aligned_bam": str(aligned_bam_path),
        "sorted_bam": str(sorted_bam_path),
        "bam_index": str(bam_index_path),
        "sorted_bam_size_bytes": sorted_bam_size,
        "bam_index_size_bytes": bam_index_size,
    }

    logger.info(f"Mock sorted BAM written to: {sorted_bam_path}")
    logger.info(f"Mock BAM index written to: {bam_index_path}")

    return state


if __name__ == "__main__":
    import logging

    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
    from pipeline.stage_02_align_data import run_stage as run_stage_02_align_data
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_03_test")

    test_config = load_config("config/config.yaml")
    validate_config(test_config)
    test_paths = initialize_run_paths(test_config)
    test_state = initialize_state(test_config, "config/config.yaml", test_paths)

    test_state = run_stage_01_load_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_02_align_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 03 completed successfully.")
    print(test_state["stage_outputs"]["stage_03_process_bam"])