"""
Stage 10: Interpret non-coding-track variants.

Version 2 responsibilities:
- read the non-coding-track table from Stage 08
- apply lightweight interpretation heuristics for non-coding variants
- write an interpreted non-coding-track output table
- update track summaries and stage_outputs in state

This stage does not perform production-grade regulatory interpretation.
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


def validate_noncoding_track_table(state: dict[str, Any]) -> Path:
    """
    Validate the non-coding-track table artifact from Stage 08.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    Path
        Path to the non-coding-track table.

    Raises
    ------
    ValueError
        If the non-coding-track table path is missing.
    FileNotFoundError
        If the non-coding-track table file does not exist.
    """
    noncoding_track_table = state["artifacts"].get("noncoding_track_table")
    if not noncoding_track_table:
        raise ValueError("Stage 10 requires artifacts.noncoding_track_table.")

    noncoding_track_path = Path(noncoding_track_table)
    if not noncoding_track_path.exists():
        raise FileNotFoundError(f"Non-coding-track table not found: {noncoding_track_path}")

    return noncoding_track_path


def load_noncoding_track_table(noncoding_track_path: Path) -> pd.DataFrame:
    """
    Load the non-coding-track TSV into a DataFrame.

    Parameters
    ----------
    noncoding_track_path : Path
        Path to the non-coding-track TSV.

    Returns
    -------
    pd.DataFrame
        Non-coding-track DataFrame.
    """
    return pd.read_csv(noncoding_track_path, sep="\t")


def assign_noncoding_priority(row: pd.Series, use_alphagenome: bool) -> tuple[str, int]:
    """
    Assign a lightweight interpretation label and numeric priority.

    Priority logic:
    - splice-relevant non-coding variants with strong SpliceAI support -> highest
    - regulatory variants -> next
    - optional AlphaGenome-style boost can elevate certain variants
    - remaining non-coding variants -> lower

    Parameters
    ----------
    row : pd.Series
        Non-coding-track row.
    use_alphagenome : bool
        Whether AlphaGenome-style support is enabled in config.

    Returns
    -------
    tuple[str, int]
        Interpretation label and priority rank (lower is stronger).
    """
    consequence = str(row.get("consequence", ""))
    clinvar = str(row.get("clinvar_classification", ""))
    spliceai = row.get("spliceai_score")

    spliceai_value = 0.0
    if pd.notna(spliceai):
        spliceai_value = float(spliceai)

    if consequence in {"intronic", "splice_region", "splice_site"} and spliceai_value >= 0.5:
        return "splice_relevant_noncoding", 1

    if consequence == "regulatory":
        if use_alphagenome:
            return "regulatory_candidate_with_ai_path", 2
        return "regulatory_candidate", 3

    if clinvar in {"pathogenic", "likely_pathogenic"}:
        return "clinically_flagged_noncoding", 2

    if clinvar == "uncertain_significance":
        return "vus_noncoding", 4

    return "lower_priority_noncoding", 5


def interpret_noncoding_variants(noncoding_df: pd.DataFrame, use_alphagenome: bool) -> pd.DataFrame:
    """
    Apply lightweight non-coding interpretation logic.

    Parameters
    ----------
    noncoding_df : pd.DataFrame
        Non-coding-track DataFrame.
    use_alphagenome : bool
        Whether AlphaGenome-style support is enabled.

    Returns
    -------
    pd.DataFrame
        Interpreted non-coding-track DataFrame.
    """
    interpreted_df = noncoding_df.copy()

    interpretation_results = interpreted_df.apply(
        lambda row: assign_noncoding_priority(row, use_alphagenome),
        axis=1,
    )
    interpreted_df["noncoding_interpretation"] = [result[0] for result in interpretation_results]
    interpreted_df["noncoding_priority_rank"] = [result[1] for result in interpretation_results]

    interpreted_df = interpreted_df.sort_values(
        by=["noncoding_priority_rank", "gene_symbol", "chromosome", "position"],
        ascending=[True, True, True, True],
    ).reset_index(drop=True)

    return interpreted_df


def write_interpreted_noncoding_output(
    interpreted_df: pd.DataFrame,
    paths: dict[str, Path | str],
) -> Path:
    """
    Write interpreted non-coding variants to the run final directory.

    Parameters
    ----------
    interpreted_df : pd.DataFrame
        Interpreted non-coding-track DataFrame.
    paths : dict[str, Path | str]
        Resolved pipeline paths.

    Returns
    -------
    Path
        Output path for interpreted non-coding variants.
    """
    output_path = Path(paths["interpreted_noncoding_table"])
    interpreted_df.to_csv(output_path, sep="\t", index=False)
    return output_path


def build_noncoding_summary(interpreted_df: pd.DataFrame, use_alphagenome: bool) -> dict[str, Any]:
    """
    Build a compact non-coding-track interpretation summary.

    Parameters
    ----------
    interpreted_df : pd.DataFrame
        Interpreted non-coding-track DataFrame.
    use_alphagenome : bool
        Whether AlphaGenome-style support is enabled.

    Returns
    -------
    dict[str, Any]
        Non-coding-track summary dictionary.
    """
    interpretation_counts = interpreted_df["noncoding_interpretation"].value_counts().to_dict()
    gene_count = int(interpreted_df["gene_symbol"].nunique()) if not interpreted_df.empty else 0

    return {
        "variant_count": len(interpreted_df),
        "gene_count": gene_count,
        "alphagenome_used": use_alphagenome,
        "interpretation_counts": interpretation_counts,
    }


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 10: interpret non-coding variants.

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
    logger.info("Stage 10: interpreting non-coding-track variants.")

    noncoding_track_path = validate_noncoding_track_table(state)
    noncoding_df = load_noncoding_track_table(noncoding_track_path)

    use_alphagenome = bool(config["interpretation"]["noncoding"]["use_alphagenome"])

    interpreted_df = interpret_noncoding_variants(noncoding_df, use_alphagenome)
    output_path = write_interpreted_noncoding_output(interpreted_df, paths)

    summary = build_noncoding_summary(interpreted_df, use_alphagenome)
    output_size = output_path.stat().st_size

    state["artifacts"]["interpreted_noncoding_table"] = str(output_path)
    state["tracks"]["noncoding"] = {
        **state["tracks"].get("noncoding", {}),
        "table_path": str(output_path),
        "variant_count": summary["variant_count"],
        "gene_count": summary["gene_count"],
        "alphagenome_used": summary["alphagenome_used"],
        "prioritization_summary": summary["interpretation_counts"],
    }
    state["stage_outputs"]["stage_10_interpret_noncoding"] = {
        "status": "success",
        "noncoding_track_table": str(noncoding_track_path),
        "interpreted_noncoding_table": str(output_path),
        "variant_count": summary["variant_count"],
        "gene_count": summary["gene_count"],
        "alphagenome_used": summary["alphagenome_used"],
        "interpretation_counts": summary["interpretation_counts"],
        "output_size_bytes": output_size,
    }

    logger.info(f"Interpreted non-coding table written to: {output_path}")
    logger.info(f"Non-coding interpreted variant count: {summary['variant_count']}")
    logger.info(f"Non-coding gene count: {summary['gene_count']}")

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
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_10_test")

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
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 10 completed successfully.")
    print(test_state["stage_outputs"]["stage_10_interpret_noncoding"])