"""
Stage 02: Align sequencing reads.

Version 2 responsibilities:
- operate in full_pipeline mode
- validate FASTQ inputs from the nested state contract
- create a mock aligned BAM artifact for framework demonstration
- record alignment QC summaries
- update artifacts and stage_outputs in state

This stage does not perform real BWA-MEM alignment inside the framework repo.
Instead, it creates a lightweight placeholder artifact that preserves:
- stage boundaries
- artifact creation
- state transitions
- logging and reproducibility
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def validate_fastq_inputs(state: dict[str, Any]) -> tuple[Path, Path]:
    """
    Validate FASTQ inputs required for full_pipeline mode.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    tuple[Path, Path]
        FASTQ R1 and FASTQ R2 paths.

    Raises
    ------
    ValueError
        If FASTQ inputs are missing.
    FileNotFoundError
        If FASTQ files do not exist.
    """
    fastq_1 = state["inputs"].get("fastq_1")
    fastq_2 = state["inputs"].get("fastq_2")

    if not fastq_1 or not fastq_2:
        raise ValueError("Stage 02 requires inputs.fastq_1 and inputs.fastq_2 in full_pipeline mode.")

    fastq_1_path = Path(fastq_1)
    fastq_2_path = Path(fastq_2)

    if not fastq_1_path.exists():
        raise FileNotFoundError(f"FASTQ R1 not found: {fastq_1_path}")
    if not fastq_2_path.exists():
        raise FileNotFoundError(f"FASTQ R2 not found: {fastq_2_path}")

    return fastq_1_path, fastq_2_path


def count_fastq_reads(fastq_path: Path) -> int:
    """
    Estimate read count from a FASTQ file.

    FASTQ format uses 4 lines per record.

    Parameters
    ----------
    fastq_path : Path
        FASTQ file path.

    Returns
    -------
    int
        Estimated number of reads.
    """
    line_count = 0
    with fastq_path.open("r", encoding="utf-8") as handle:
        for _ in handle:
            line_count += 1

    return line_count // 4


def write_mock_aligned_bam(
    output_path: Path,
    sample_id: str,
    fastq_1_path: Path,
    fastq_2_path: Path,
    read_count_r1: int,
    read_count_r2: int,
    reference_genome: str,
) -> None:
    """
    Write a mock aligned BAM placeholder artifact.

    Parameters
    ----------
    output_path : Path
        Destination BAM path.
    sample_id : str
        Sample identifier.
    fastq_1_path : Path
        FASTQ R1 path.
    fastq_2_path : Path
        FASTQ R2 path.
    read_count_r1 : int
        Read count for FASTQ R1.
    read_count_r2 : int
        Read count for FASTQ R2.
    reference_genome : str
        Reference genome label.
    """
    content = [
        "MOCK_BAM_PLACEHOLDER",
        f"sample_id={sample_id}",
        f"reference_genome={reference_genome}",
        f"fastq_1={fastq_1_path}",
        f"fastq_2={fastq_2_path}",
        f"read_count_r1={read_count_r1}",
        f"read_count_r2={read_count_r2}",
        "alignment_tool=bwa_mem_placeholder",
        "status=aligned_mock_output",
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
    Execute Stage 02: align sequencing reads.

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
    logger.info("Stage 02: aligning sequencing reads.")

    execution_mode = state["run"]["mode"]
    if execution_mode != "full_pipeline":
        raise ValueError("Stage 02 should only run in full_pipeline mode.")

    fastq_1_path, fastq_2_path = validate_fastq_inputs(state)

    sample_id = state["sample"]["sample_id"]
    reference_genome = state["sample"]["reference_genome"]
    aligned_bam_path = Path(paths["aligned_bam"])

    create_mock_bam = config["alignment"]["create_mock_bam"]
    if not create_mock_bam:
        raise ValueError("Stage 02 currently requires alignment.create_mock_bam=true in framework v2.")

    read_count_r1 = count_fastq_reads(fastq_1_path)
    read_count_r2 = count_fastq_reads(fastq_2_path)

    logger.info(f"FASTQ R1 reads detected: {read_count_r1}")
    logger.info(f"FASTQ R2 reads detected: {read_count_r2}")

    write_mock_aligned_bam(
        output_path=aligned_bam_path,
        sample_id=sample_id,
        fastq_1_path=fastq_1_path,
        fastq_2_path=fastq_2_path,
        read_count_r1=read_count_r1,
        read_count_r2=read_count_r2,
        reference_genome=reference_genome,
    )

    mapping_rate = 1.0 if config["alignment"]["record_mapping_rate"] else None

    state["artifacts"]["aligned_bam"] = str(aligned_bam_path)
    state["qc"]["alignment_qc"] = {
        "alignment_completed": True,
        "mock_alignment": True,
        "read_count_r1": read_count_r1,
        "read_count_r2": read_count_r2,
        "mapping_rate": mapping_rate,
    }
    state["stage_outputs"]["stage_02_align_data"] = {
        "status": "success",
        "aligned_bam": str(aligned_bam_path),
        "read_count_r1": read_count_r1,
        "read_count_r2": read_count_r2,
        "mapping_rate": mapping_rate,
    }

    logger.info(f"Mock aligned BAM written to: {aligned_bam_path}")

    return state


if __name__ == "__main__":
    import logging

    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state
    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_02_test")

    test_config = load_config("config/config.yaml")
    validate_config(test_config)
    test_paths = initialize_run_paths(test_config)
    test_state = initialize_state(test_config, "config/config.yaml", test_paths)
    test_state = run_stage_01_load_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 02 completed successfully.")
    print(test_state["stage_outputs"]["stage_02_align_data"])