"""
Stage 12: Prepare prioritized variants for manual IGV review.

Version 2 responsibilities:
- read the prioritized variant table from Stage 11
- perform lightweight automated validation pre-checks
- generate a validation report and an IGV review candidate list
- update validation summaries and stage_outputs in state

This stage does not automate IGV itself.
Instead, it prepares a reproducible, structured handoff for optional
manual review in IGV by:
- checking table integrity
- flagging candidate loci
- emitting a review-oriented report
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def validate_prioritized_table(state: dict[str, Any]) -> Path:
    """
    Validate the prioritized variant table artifact from Stage 11.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    Path
        Path to the prioritized variant table.

    Raises
    ------
    ValueError
        If the prioritized table path is missing.
    FileNotFoundError
        If the prioritized table file does not exist.
    """
    prioritized_table = state["artifacts"].get("prioritized_table")
    if not prioritized_table:
        raise ValueError("Stage 12 requires artifacts.prioritized_table.")

    prioritized_path = Path(prioritized_table)
    if not prioritized_path.exists():
        raise FileNotFoundError(f"Prioritized variant table not found: {prioritized_path}")

    return prioritized_path


def load_prioritized_table(prioritized_path: Path) -> pd.DataFrame:
    """
    Load the prioritized variant table.

    Parameters
    ----------
    prioritized_path : Path
        Path to prioritized variant table.

    Returns
    -------
    pd.DataFrame
        Prioritized variants DataFrame.
    """
    return pd.read_csv(prioritized_path, sep="\t")


def perform_validation_prechecks(prioritized_df: pd.DataFrame) -> tuple[list[str], list[str], pd.DataFrame]:
    """
    Perform lightweight automated validation pre-checks.

    Parameters
    ----------
    prioritized_df : pd.DataFrame
        Prioritized variants DataFrame.

    Returns
    -------
    tuple[list[str], list[str], pd.DataFrame]
        Warnings, review notes, and IGV review candidate DataFrame.
    """
    warnings: list[str] = []
    review_notes: list[str] = []

    required_columns = [
        "chromosome",
        "position",
        "reference_allele",
        "alternate_allele",
        "gene_symbol",
        "variant_type",
        "final_priority_label",
        "final_priority_rank",
    ]

    missing_columns = [column for column in required_columns if column not in prioritized_df.columns]
    if missing_columns:
        warnings.append(f"Missing expected prioritized-variant columns: {', '.join(missing_columns)}")

    if prioritized_df.empty:
        warnings.append("Prioritized variant table is empty; no IGV review candidates available.")
        empty_df = prioritized_df.copy()
        return warnings, review_notes, empty_df

    if "af_gnomad" in prioritized_df.columns:
        high_af_rows = prioritized_df[prioritized_df["af_gnomad"] > 0.01]
        if not high_af_rows.empty:
            warnings.append(f"{len(high_af_rows)} prioritized variants have AF_gnomAD > 0.01 and may warrant extra scrutiny.")

    if "clinvar_classification" in prioritized_df.columns:
        conflicting_rows = prioritized_df[
            prioritized_df["clinvar_classification"].isin(["benign", "likely_benign"])
            & prioritized_df["final_priority_rank"].le(2)
        ] if "final_priority_rank" in prioritized_df.columns else prioritized_df.iloc[0:0]
        if not conflicting_rows.empty:
            warnings.append(f"{len(conflicting_rows)} variants appear high-priority despite benign-like ClinVar labels.")

    candidate_df = prioritized_df.copy()

    if "final_priority_rank" in candidate_df.columns:
        candidate_df = candidate_df[candidate_df["final_priority_rank"] <= 3].copy()

    if "track" in candidate_df.columns:
        candidate_df["manual_review_reason"] = candidate_df["track"].map({
            "coding": "review coding candidate in IGV for depth, balance, and alignment context",
            "noncoding": "review non-coding candidate in IGV for local alignment context",
        }).fillna("review candidate in IGV")

    if "consequence" in candidate_df.columns and "manual_review_reason" in candidate_df.columns:
        splice_mask = candidate_df["consequence"].isin(["splice_site", "splice_region"])
        candidate_df.loc[splice_mask, "manual_review_reason"] = (
            "review splice-relevant candidate in IGV for read support and nearby alignment context"
        )

    review_notes.append("IGV review is manual and is not automated by this framework pipeline.")
    review_notes.append("Recommended IGV checks: read depth, allele balance, strand bias, and local alignment artifacts.")
    review_notes.append("Use the BAM/BAM index and prioritized loci generated by the run for targeted review.")

    return warnings, review_notes, candidate_df


def write_validation_outputs(
    candidate_df: pd.DataFrame,
    warnings: list[str],
    review_notes: list[str],
    paths: dict[str, Path | str],
) -> tuple[Path, Path]:
    """
    Write validation outputs for manual IGV review.

    Parameters
    ----------
    candidate_df : pd.DataFrame
        Candidate variants for IGV review.
    warnings : list[str]
        Validation warnings.
    review_notes : list[str]
        Review guidance notes.
    paths : dict[str, Path | str]
        Resolved pipeline paths.

    Returns
    -------
    tuple[Path, Path]
        Validation notes path and IGV review candidate TSV path.
    """
    validation_notes_path = Path(paths["validation_notes"])
    igv_candidates_path = Path(paths["run_validation_dir"]) / "igv_review_candidates.tsv"

    candidate_df.to_csv(igv_candidates_path, sep="\t", index=False)

    lines = [
        "Manual IGV Review Preparation Report",
        "===================================",
        "",
        "Purpose:",
        "This report prepares prioritized variants for optional manual review in IGV.",
        "",
        "Validation Model:",
        "- automated pre-checks were performed by the pipeline",
        "- IGV inspection itself remains a manual user-driven step",
        "",
        "Warnings:",
    ]

    if warnings:
        lines.extend([f"- {warning}" for warning in warnings])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "Review Notes:",
    ])
    lines.extend([f"- {note}" for note in review_notes])

    lines.extend([
        "",
        "Output Files:",
        f"- IGV candidate list: {igv_candidates_path}",
    ])

    with validation_notes_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    return validation_notes_path, igv_candidates_path


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 12: prepare variants for manual IGV review.

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
    logger.info("Stage 12: preparing prioritized variants for manual IGV review.")

    if not bool(config["validation_step"]["enable_validation"]):
        raise ValueError("Stage 12 requires validation_step.enable_validation=true.")

    prioritized_path = validate_prioritized_table(state)
    prioritized_df = load_prioritized_table(prioritized_path)

    warnings, review_notes, candidate_df = perform_validation_prechecks(prioritized_df)
    validation_notes_path, igv_candidates_path = write_validation_outputs(
        candidate_df=candidate_df,
        warnings=warnings,
        review_notes=review_notes,
        paths=paths,
    )

    validation_notes_size = validation_notes_path.stat().st_size
    candidate_count = len(candidate_df)

    state["artifacts"]["validation_notes"] = str(validation_notes_path)
    state["qc"]["validation_qc"] = {
        "validation_completed": True,
        "manual_igv_review_required": True,
        "candidate_count": candidate_count,
        "warning_count": len(warnings),
        "igv_candidates_path": str(igv_candidates_path),
    }
    state["stage_outputs"]["stage_12_validate_variants"] = {
        "status": "success",
        "prioritized_table": str(prioritized_path),
        "validation_notes": str(validation_notes_path),
        "igv_review_candidates": str(igv_candidates_path),
        "candidate_count": candidate_count,
        "warning_count": len(warnings),
        "output_size_bytes": validation_notes_size,
    }

    state["warnings"].extend(warnings)

    logger.info(f"Validation notes written to: {validation_notes_path}")
    logger.info(f"IGV review candidates written to: {igv_candidates_path}")
    logger.info(f"Manual IGV review candidate count: {candidate_count}")

    return state


if __name__ == "__main__":
    import logging

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
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_12_test")

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
    test_state = run_stage_06_normalize_vcf(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_07_annotate_variants(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_08_filter_and_partition(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_09_interpret_coding(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_10_interpret_noncoding(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_11_prioritize_variants(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 12 completed successfully.")
    print(test_state["stage_outputs"]["stage_12_validate_variants"])