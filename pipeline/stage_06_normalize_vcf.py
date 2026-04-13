"""
Stage 06: Normalize VCF.

Version 2 responsibilities:
- support both full_pipeline and annotation_only modes
- read the correct VCF input source based on execution mode
- create a normalized VCF artifact
- record normalization QC summaries
- update artifacts and stage_outputs in state

This stage does not perform real GATK normalization inside the framework repo.
Instead, it creates a lightweight normalized VCF that preserves:
- stage boundaries
- artifact creation
- state transitions
- logging and reproducibility
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def get_input_vcf_for_mode(state: dict[str, Any]) -> Path:
    """
    Resolve the correct input VCF path based on execution mode.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    Path
        Input VCF path for normalization.

    Raises
    ------
    ValueError
        If the required VCF path is missing.
    FileNotFoundError
        If the required VCF file does not exist.
    """
    execution_mode = state["run"]["mode"]

    if execution_mode == "full_pipeline":
        input_vcf = state["artifacts"].get("raw_vcf")
        if not input_vcf:
            raise ValueError("Stage 06 requires artifacts.raw_vcf in full_pipeline mode.")
    elif execution_mode == "annotation_only":
        input_vcf = state["inputs"].get("input_vcf")
        if not input_vcf:
            raise ValueError("Stage 06 requires inputs.input_vcf in annotation_only mode.")
    else:
        raise ValueError(f"Unsupported execution mode in Stage 06: {execution_mode}")

    input_vcf_path = Path(input_vcf)
    if not input_vcf_path.exists():
        raise FileNotFoundError(f"Input VCF for Stage 06 not found: {input_vcf_path}")

    return input_vcf_path


def normalize_variant_line(line: str, normalize_chromosome_prefix: bool) -> str:
    """
    Apply lightweight normalization to a VCF variant line.

    Parameters
    ----------
    line : str
        Raw VCF variant line.
    normalize_chromosome_prefix : bool
        Whether chromosome labels should be normalized to 'chr' format.

    Returns
    -------
    str
        Normalized VCF variant line.
    """
    fields = line.rstrip("\n").split("\t")
    chromosome = fields[0]

    if normalize_chromosome_prefix and not chromosome.lower().startswith("chr"):
        fields[0] = f"chr{chromosome}"

    return "\t".join(fields)


def write_normalized_vcf(
    input_vcf_path: Path,
    output_vcf_path: Path,
    normalize_chromosome_prefix: bool,
) -> tuple[int, int]:
    """
    Write a normalized VCF artifact.

    Parameters
    ----------
    input_vcf_path : Path
        Source VCF path.
    output_vcf_path : Path
        Destination normalized VCF path.
    normalize_chromosome_prefix : bool
        Whether chromosome labels should be normalized.

    Returns
    -------
    tuple[int, int]
        Variant count written and malformed line count skipped.
    """
    variant_count = 0
    malformed_count = 0

    with input_vcf_path.open("r", encoding="utf-8") as input_handle, output_vcf_path.open("w", encoding="utf-8") as output_handle:
        for line in input_handle:
            if line.startswith("##"):
                output_handle.write(line)
                continue

            if line.startswith("#CHROM"):
                output_handle.write(line)
                continue

            stripped = line.strip()
            if not stripped:
                continue

            fields = stripped.split("\t")
            if len(fields) < 8:
                malformed_count += 1
                continue

            normalized_line = normalize_variant_line(line, normalize_chromosome_prefix)
            output_handle.write(normalized_line + "\n")
            variant_count += 1

    return variant_count, malformed_count


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 06: normalize VCF.

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
    """
    logger.info("Stage 06: normalizing VCF.")

    input_vcf_path = get_input_vcf_for_mode(state)
    normalized_vcf_path = Path(paths["normalized_vcf"])

    normalize_chromosome_prefix = bool(config["vcf_normalization"]["normalize_chromosome_prefix"])

    variant_count, malformed_count = write_normalized_vcf(
        input_vcf_path=input_vcf_path,
        output_vcf_path=normalized_vcf_path,
        normalize_chromosome_prefix=normalize_chromosome_prefix,
    )

    normalized_vcf_size = normalized_vcf_path.stat().st_size
    execution_mode = state["run"]["mode"]

    variant_calling_qc_prior = state["qc"].get("variant_calling_qc", {})

    state["artifacts"]["normalized_vcf"] = str(normalized_vcf_path)
    state["qc"]["variant_calling_qc"] = {
        **variant_calling_qc_prior,
        "vcf_normalization_completed": True,
        "normalized_vcf_created": True,
        "normalized_variant_count": variant_count,
        "malformed_records_skipped": malformed_count,
        "normalized_vcf_size_bytes": normalized_vcf_size,
        "normalize_chromosome_prefix": normalize_chromosome_prefix,
    }
    state["stage_outputs"]["stage_06_normalize_vcf"] = {
        "status": "success",
        "execution_mode": execution_mode,
        "input_vcf": str(input_vcf_path),
        "normalized_vcf": str(normalized_vcf_path),
        "normalized_variant_count": variant_count,
        "malformed_records_skipped": malformed_count,
        "normalized_vcf_size_bytes": normalized_vcf_size,
    }

    logger.info(f"Normalized VCF written to: {normalized_vcf_path}")
    logger.info(f"Normalized variant count: {variant_count}")
    logger.info(f"Malformed records skipped: {malformed_count}")

    return state


if __name__ == "__main__":
    import logging

    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
    from pipeline.stage_02_align_data import run_stage as run_stage_02_align_data
    from pipeline.stage_03_process_bam import run_stage as run_stage_03_process_bam
    from pipeline.stage_04_qc_aligned_reads import run_stage as run_stage_04_qc_aligned_reads
    from pipeline.stage_05_call_variants import run_stage as run_stage_05_call_variants
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_06_test")

    test_config = load_config("config/config.yaml")
    validate_config(test_config)
    test_paths = initialize_run_paths(test_config)
    test_state = initialize_state(test_config, "config/config.yaml", test_paths)

    test_state = run_stage_01_load_data(test_config, test_paths, test_logger, test_state)
    if test_state["run"]["mode"] == "full_pipeline":
        test_state = run_stage_02_align_data(test_config, test_paths, test_logger, test_state)
        test_state = run_stage_03_process_bam(test_config, test_paths, test_logger, test_state)
        test_state = run_stage_04_qc_aligned_reads(test_config, test_paths, test_logger, test_state)
        test_state = run_stage_05_call_variants(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 06 completed successfully.")
    print(test_state["stage_outputs"]["stage_06_normalize_vcf"])