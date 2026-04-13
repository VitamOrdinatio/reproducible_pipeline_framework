"""
Stage 09: Interpret coding-track variants.

Version 2 responsibilities:
- read the coding-track table from Stage 08
- apply lightweight interpretation heuristics for coding variants
- write an interpreted coding-track output table
- update track summaries and stage_outputs in state

This stage does not perform production-grade ACMG-style interpretation.
Instead, it creates a lightweight interpretation layer that preserves:
- stage boundaries
- artifact creation
- state transitions
- reproducibility
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def validate_coding_track_table(state: dict[str, Any]) -> Path:
    """
    Validate the coding-track table artifact from Stage 08.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    Path
        Path to the coding-track table.

    Raises
    ------
    ValueError
        If the coding-track table path is missing.
    FileNotFoundError
        If the coding-track table file does not exist.
    """
    coding_track_table = state["artifacts"].get("coding_track_table")
    if not coding_track_table:
        raise ValueError("Stage 09 requires artifacts.coding_track_table.")

    coding_track_path = Path(coding_track_table)
    if not coding_track_path.exists():
        raise FileNotFoundError(f"Coding-track table not found: {coding_track_path}")

    return coding_track_path


def load_coding_track_table(coding_track_path: Path) -> pd.DataFrame:
    """
    Load the coding-track TSV into a DataFrame.

    Parameters
    ----------
    coding_track_path : Path
        Path to the coding-track TSV.

    Returns
    -------
    pd.DataFrame
        Coding-track DataFrame.
    """
    return pd.read_csv(coding_track_path, sep="\t")


def assign_coding_priority(row: pd.Series) -> tuple[str, int]:
    """
    Assign a lightweight interpretation label and numeric priority.

    Priority logic:
    - pathogenic splice/nonsense -> highest
    - likely pathogenic -> next
    - VUS missense with strong AlphaMissense support -> next
    - other coding variants -> lower

    Parameters
    ----------
    row : pd.Series
        Coding-track row.

    Returns
    -------
    tuple[str, int]
        Interpretation label and priority rank (lower is stronger).
    """
    consequence = str(row.get("consequence", ""))
    clinvar = str(row.get("clinvar_classification", ""))
    alphamissense = row.get("alphamissense_score")

    if clinvar == "pathogenic" or consequence in {"nonsense", "splice_site", "frameshift"}:
        return "prioritized_pathogenic_like", 1

    if clinvar == "likely_pathogenic":
        return "prioritized_likely_pathogenic", 2

    if consequence == "missense" and pd.notna(alphamissense) and float(alphamissense) >= 0.8:
        return "vus_with_ai_support", 3

    if clinvar == "uncertain_significance":
        return "vus_low_support", 4

    return "lower_priority_coding", 5


def interpret_coding_variants(coding_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply lightweight coding interpretation logic.

    Parameters
    ----------
    coding_df : pd.DataFrame
        Coding-track DataFrame.

    Returns
    -------
    pd.DataFrame
        Interpreted coding-track DataFrame.
    """
    interpreted_df = coding_df.copy()

    interpretation_results = interpreted_df.apply(assign_coding_priority, axis=1)
    interpreted_df["coding_interpretation"] = [result[0] for result in interpretation_results]
    interpreted_df["coding_priority_rank"] = [result[1] for result in interpretation_results]

    interpreted_df = interpreted_df.sort_values(
        by=["coding_priority_rank", "gene_symbol", "chromosome", "position"],
        ascending=[True, True, True, True],
    ).reset_index(drop=True)

    return interpreted_df


def write_interpreted_coding_output(
    interpreted_df: pd.DataFrame,
    paths: dict[str, Path | str],
) -> Path:
    """
    Write interpreted coding variants to the run final directory.

    Parameters
    ----------
    interpreted_df : pd.DataFrame
        Interpreted coding-track DataFrame.
    paths : dict[str, Path | str]
        Resolved pipeline paths.

    Returns
    -------
    Path
        Output path for interpreted coding variants.
    """
    output_path = Path(paths["interpreted_coding_table"])
    interpreted_df.to_csv(output_path, sep="\t", index=False)
    return output_path


def build_coding_summary(interpreted_df: pd.DataFrame) -> dict[str, Any]:
    """
    Build a compact coding-track interpretation summary.

    Parameters
    ----------
    interpreted_df : pd.DataFrame
        Interpreted coding-track DataFrame.

    Returns
    -------
    dict[str, Any]
        Coding-track summary dictionary.
    """
    interpretation_counts = interpreted_df["coding_interpretation"].value_counts().to_dict()
    top_gene_count = int(interpreted_df["gene_symbol"].nunique()) if not interpreted_df.empty else 0

    return {
        "variant_count": len(interpreted_df),
        "gene_count": top_gene_count,
        "interpretation_counts": interpretation_counts,
    }


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 09: interpret coding variants.

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
    logger.info("Stage 09: interpreting coding-track variants.")

    coding_track_path = validate_coding_track_table(state)
    coding_df = load_coding_track_table(coding_track_path)
    interpreted_df = interpret_coding_variants(coding_df)
    output_path = write_interpreted_coding_output(interpreted_df, paths)

    summary = build_coding_summary(interpreted_df)
    output_size = output_path.stat().st_size

    state["artifacts"]["interpreted_coding_table"] = str(output_path)
    state["tracks"]["coding"] = {
        **state["tracks"].get("coding", {}),
        "table_path": str(output_path),
        "variant_count": summary["variant_count"],
        "gene_count": summary["gene_count"],
        "prioritization_summary": summary["interpretation_counts"],
    }
    state["stage_outputs"]["stage_09_interpret_coding"] = {
        "status": "success",
        "coding_track_table": str(coding_track_path),
        "interpreted_coding_table": str(output_path),
        "variant_count": summary["variant_count"],
        "gene_count": summary["gene_count"],
        "interpretation_counts": summary["interpretation_counts"],
        "output_size_bytes": output_size,
    }

    logger.info(f"Interpreted coding table written to: {output_path}")
    logger.info(f"Coding interpreted variant count: {summary['variant_count']}")
    logger.info(f"Coding gene count: {summary['gene_count']}")

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
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_09_test")

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
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 09 completed successfully.")
    print(test_state["stage_outputs"]["stage_09_interpret_coding"])