"""
Stage 05: Call variants from processed BAM artifacts.

Version 2 responsibilities:
- operate in full_pipeline mode
- validate sorted BAM and BAM index artifacts from Stage 03
- create a mock raw VCF artifact
- record variant-calling QC summaries
- update artifacts and stage_outputs in state

This stage does not perform real GATK variant calling inside the framework repo.
Instead, it creates a lightweight placeholder VCF that preserves:
- stage boundaries
- artifact creation
- state transitions
- logging and reproducibility
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def validate_bam_inputs(state: dict[str, Any]) -> tuple[Path, Path]:
    """
    Validate sorted BAM and BAM index artifacts required for variant calling.

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
        raise ValueError("Stage 05 requires artifacts.sorted_bam.")
    if not bam_index:
        raise ValueError("Stage 05 requires artifacts.bam_index.")

    sorted_bam_path = Path(sorted_bam)
    bam_index_path = Path(bam_index)

    if not sorted_bam_path.exists():
        raise FileNotFoundError(f"Sorted BAM not found: {sorted_bam_path}")
    if not bam_index_path.exists():
        raise FileNotFoundError(f"BAM index not found: {bam_index_path}")

    return sorted_bam_path, bam_index_path


def build_mock_vcf_records() -> list[str]:
    """
    Build lightweight mock VCF variant records.

    Returns
    -------
    list[str]
        Mock VCF body lines.
    """
    return [
        "1\t123456\t.\tA\tG\t50\tPASS\tTYPE=SNV",
        "1\t123789\t.\tC\tT\t60\tPASS\tTYPE=SNV",
        "2\t987654\t.\tG\tA\t20\tq10\tTYPE=SNV",
        "2\t555000\t.\tT\tC\t90\tPASS\tTYPE=SNV",
        "X\t111111\t.\tG\tT\t70\tPASS\tTYPE=SNV",
    ]


def write_mock_raw_vcf(
    output_path: Path,
    reference_genome: str,
    sorted_bam_path: Path,
    bam_index_path: Path,
    sample_id: str,
    emit_snv: bool,
    emit_indel: bool,
) -> int:
    """
    Write a mock raw VCF artifact.

    Parameters
    ----------
    output_path : Path
        Destination raw VCF path.
    reference_genome : str
        Reference genome label.
    sorted_bam_path : Path
        Sorted BAM path.
    bam_index_path : Path
        BAM index path.
    sample_id : str
        Sample identifier.
    emit_snv : bool
        Whether SNVs are enabled in config.
    emit_indel : bool
        Whether indels are enabled in config.

    Returns
    -------
    int
        Number of variant records written.
    """
    header_lines = [
        "##fileformat=VCFv4.2",
        "##source=gatk_haplotypecaller_placeholder",
        f"##reference={reference_genome}",
        f"##sample_id={sample_id}",
        f"##sorted_bam={sorted_bam_path}",
        f"##bam_index={bam_index_path}",
        f"##emit_snv={emit_snv}",
        f"##emit_indel={emit_indel}",
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO",
    ]

    records = build_mock_vcf_records()

    with output_path.open("w", encoding="utf-8") as handle:
        for line in header_lines:
            handle.write(line + "\n")
        for record in records:
            handle.write(record + "\n")

    return len(records)


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 05: call variants.

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
        If execution mode is incorrect or required config/state keys are missing.
    """
    logger.info("Stage 05: calling variants.")

    execution_mode = state["run"]["mode"]
    if execution_mode != "full_pipeline":
        raise ValueError("Stage 05 should only run in full_pipeline mode.")

    sorted_bam_path, bam_index_path = validate_bam_inputs(state)

    if not config["variant_calling"]["create_mock_raw_vcf"]:
        raise ValueError("Stage 05 currently requires variant_calling.create_mock_raw_vcf=true.")

    reference_genome = state["sample"]["reference_genome"]
    sample_id = state["sample"]["sample_id"]
    raw_vcf_path = Path(paths["raw_vcf"])

    emit_snv = bool(config["variant_calling"]["emit_snv"])
    emit_indel = bool(config["variant_calling"]["emit_indel"])

    variant_count = write_mock_raw_vcf(
        output_path=raw_vcf_path,
        reference_genome=reference_genome,
        sorted_bam_path=sorted_bam_path,
        bam_index_path=bam_index_path,
        sample_id=sample_id,
        emit_snv=emit_snv,
        emit_indel=emit_indel,
    )

    raw_vcf_size = raw_vcf_path.stat().st_size

    state["artifacts"]["raw_vcf"] = str(raw_vcf_path)
    state["qc"]["variant_calling_qc"] = {
        "variant_calling_completed": True,
        "mock_variant_calling": True,
        "raw_vcf_created": True,
        "variant_count": variant_count,
        "raw_vcf_size_bytes": raw_vcf_size,
        "emit_snv": emit_snv,
        "emit_indel": emit_indel,
    }
    state["stage_outputs"]["stage_05_call_variants"] = {
        "status": "success",
        "sorted_bam": str(sorted_bam_path),
        "bam_index": str(bam_index_path),
        "raw_vcf": str(raw_vcf_path),
        "variant_count": variant_count,
        "raw_vcf_size_bytes": raw_vcf_size,
    }

    logger.info(f"Mock raw VCF written to: {raw_vcf_path}")
    logger.info(f"Variant count: {variant_count}")

    return state


if __name__ == "__main__":
    import logging

    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
    from pipeline.stage_02_align_data import run_stage as run_stage_02_align_data
    from pipeline.stage_03_process_bam import run_stage as run_stage_03_process_bam
    from pipeline.stage_04_qc_aligned_reads import run_stage as run_stage_04_qc_aligned_reads
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_05_test")

    test_config = load_config("config/config.yaml")
    validate_config(test_config)
    test_paths = initialize_run_paths(test_config)
    test_state = initialize_state(test_config, "config/config.yaml", test_paths)

    test_state = run_stage_01_load_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_02_align_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_03_process_bam(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_04_qc_aligned_reads(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 05 completed successfully.")
    print(test_state["stage_outputs"]["stage_05_call_variants"])