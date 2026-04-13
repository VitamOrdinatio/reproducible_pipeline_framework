"""
Stage 11: Prioritize interpreted variants across coding and non-coding tracks.

Version 2 responsibilities:
- read interpreted coding and non-coding tables
- combine both tracks into a unified prioritized variant table
- assign a final priority rank across all retained variants
- write prioritized output
- update artifacts, summaries, and stage_outputs in state

This stage uses lightweight framework-safe prioritization logic and is not
intended to reproduce full clinical-grade variant ranking.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def validate_interpreted_tables(state: dict[str, Any]) -> tuple[Path, Path]:
    """
    Validate interpreted coding and non-coding table artifacts.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    tuple[Path, Path]
        Paths to interpreted coding and interpreted non-coding tables.

    Raises
    ------
    ValueError
        If required artifact paths are missing.
    FileNotFoundError
        If required files do not exist.
    """
    interpreted_coding = state["artifacts"].get("interpreted_coding_table")
    interpreted_noncoding = state["artifacts"].get("interpreted_noncoding_table")

    if not interpreted_coding:
        raise ValueError("Stage 11 requires artifacts.interpreted_coding_table.")
    if not interpreted_noncoding:
        raise ValueError("Stage 11 requires artifacts.interpreted_noncoding_table.")

    interpreted_coding_path = Path(interpreted_coding)
    interpreted_noncoding_path = Path(interpreted_noncoding)

    if not interpreted_coding_path.exists():
        raise FileNotFoundError(f"Interpreted coding table not found: {interpreted_coding_path}")
    if not interpreted_noncoding_path.exists():
        raise FileNotFoundError(f"Interpreted non-coding table not found: {interpreted_noncoding_path}")

    return interpreted_coding_path, interpreted_noncoding_path


def load_interpreted_tables(
    interpreted_coding_path: Path,
    interpreted_noncoding_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load interpreted coding and non-coding tables.

    Parameters
    ----------
    interpreted_coding_path : Path
        Path to interpreted coding table.
    interpreted_noncoding_path : Path
        Path to interpreted non-coding table.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Coding and non-coding interpreted DataFrames.
    """
    coding_df = pd.read_csv(interpreted_coding_path, sep="\t")
    noncoding_df = pd.read_csv(interpreted_noncoding_path, sep="\t")
    return coding_df, noncoding_df


def assign_final_priority(row: pd.Series) -> tuple[str, int]:
    """
    Assign final cross-track prioritization label and rank.

    Lower numeric rank indicates stronger priority.

    Parameters
    ----------
    row : pd.Series
        Combined interpreted variant row.

    Returns
    -------
    tuple[str, int]
        Final priority label and final priority rank.
    """
    variant_type = str(row.get("variant_type", ""))
    clinvar = str(row.get("clinvar_classification", ""))
    consequence = str(row.get("consequence", ""))
    af_gnomad = float(row.get("af_gnomad", 1.0))
    coding_rank = row.get("coding_priority_rank")
    noncoding_rank = row.get("noncoding_priority_rank")
    spliceai = row.get("spliceai_score")

    spliceai_value = 0.0 if pd.isna(spliceai) else float(spliceai)

    if variant_type == "coding":
        if clinvar == "pathogenic" or consequence in {"nonsense", "splice_site", "frameshift"}:
            return "tier_1_coding_high_impact", 1
        if not pd.isna(coding_rank) and int(coding_rank) <= 2:
            return "tier_2_coding_supported", 2
        if af_gnomad <= 0.001:
            return "tier_3_coding_rare", 3
        return "tier_4_coding_lower", 4

    if variant_type == "non-coding":
        if spliceai_value >= 0.5:
            return "tier_2_noncoding_splice_relevant", 2
        if not pd.isna(noncoding_rank) and int(noncoding_rank) <= 3:
            return "tier_3_noncoding_supported", 3
        if af_gnomad <= 0.01:
            return "tier_4_noncoding_rare", 4
        return "tier_5_noncoding_lower", 5

    return "tier_9_unclassified", 9


def combine_and_prioritize(
    coding_df: pd.DataFrame,
    noncoding_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Combine coding and non-coding interpreted variants and assign final priority.

    Parameters
    ----------
    coding_df : pd.DataFrame
        Interpreted coding variants.
    noncoding_df : pd.DataFrame
        Interpreted non-coding variants.

    Returns
    -------
    pd.DataFrame
        Combined prioritized variants DataFrame.
    """
    coding_combined = coding_df.copy()
    noncoding_combined = noncoding_df.copy()

    coding_combined["track"] = "coding"
    noncoding_combined["track"] = "noncoding"

    combined_df = pd.concat([coding_combined, noncoding_combined], ignore_index=True, sort=False)

    priority_results = combined_df.apply(assign_final_priority, axis=1)
    combined_df["final_priority_label"] = [result[0] for result in priority_results]
    combined_df["final_priority_rank"] = [result[1] for result in priority_results]

    combined_df = combined_df.sort_values(
        by=["final_priority_rank", "track", "gene_symbol", "chromosome", "position"],
        ascending=[True, True, True, True, True],
    ).reset_index(drop=True)

    combined_df["final_priority_order"] = range(1, len(combined_df) + 1)

    return combined_df


def write_prioritized_output(
    prioritized_df: pd.DataFrame,
    paths: dict[str, Path | str],
) -> Path:
    """
    Write prioritized variants to the run final directory.

    Parameters
    ----------
    prioritized_df : pd.DataFrame
        Prioritized combined variants.
    paths : dict[str, Path | str]
        Resolved pipeline paths.

    Returns
    -------
    Path
        Output path for prioritized variants.
    """
    output_path = Path(paths["prioritized_table"])
    prioritized_df.to_csv(output_path, sep="\t", index=False)
    return output_path


def build_prioritization_summary(prioritized_df: pd.DataFrame) -> dict[str, Any]:
    """
    Build compact prioritization summary.

    Parameters
    ----------
    prioritized_df : pd.DataFrame
        Prioritized combined variants.

    Returns
    -------
    dict[str, Any]
        Prioritization summary dictionary.
    """
    label_counts = prioritized_df["final_priority_label"].value_counts().to_dict()
    track_counts = prioritized_df["track"].value_counts().to_dict()
    gene_count = int(prioritized_df["gene_symbol"].nunique()) if not prioritized_df.empty else 0

    return {
        "variant_count": len(prioritized_df),
        "gene_count": gene_count,
        "priority_label_counts": label_counts,
        "track_counts": track_counts,
    }


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 11: prioritize variants across tracks.

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
    logger.info("Stage 11: prioritizing variants across coding and non-coding tracks.")

    interpreted_coding_path, interpreted_noncoding_path = validate_interpreted_tables(state)
    coding_df, noncoding_df = load_interpreted_tables(interpreted_coding_path, interpreted_noncoding_path)

    prioritized_df = combine_and_prioritize(coding_df, noncoding_df)
    output_path = write_prioritized_output(prioritized_df, paths)

    summary = build_prioritization_summary(prioritized_df)
    output_size = output_path.stat().st_size

    state["artifacts"]["prioritized_table"] = str(output_path)
    state["stage_outputs"]["stage_11_prioritize_variants"] = {
        "status": "success",
        "interpreted_coding_table": str(interpreted_coding_path),
        "interpreted_noncoding_table": str(interpreted_noncoding_path),
        "prioritized_table": str(output_path),
        "variant_count": summary["variant_count"],
        "gene_count": summary["gene_count"],
        "priority_label_counts": summary["priority_label_counts"],
        "track_counts": summary["track_counts"],
        "output_size_bytes": output_size,
    }

    logger.info(f"Prioritized variant table written to: {output_path}")
    logger.info(f"Prioritized variant count: {summary['variant_count']}")
    logger.info(f"Prioritized gene count: {summary['gene_count']}")

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
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_11_test")

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
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 11 completed successfully.")
    print(test_state["stage_outputs"]["stage_11_prioritize_variants"])