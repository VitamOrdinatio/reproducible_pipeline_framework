"""
Stage 05: Filter and prioritize annotated variant data.

Version 1 responsibilities:
- confirm that Stage 04 produced an annotated DataFrame
- apply simple prioritization filters from config
- write final prioritized output to results/runs/<run_id>/final/
- store prioritized DataFrame in state
- record filtering and prioritization summary in state

This stage uses simplified demonstration logic for Version 1.
It is intended to make the pipeline runnable and structurally realistic,
not clinically validated.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


HIGH_IMPACT_CONSEQUENCES = {
    "nonsense",
    "frameshift",
    "splice_site",
}


PROTEIN_CODING_CONSEQUENCES = {
    "missense",
    "nonsense",
    "frameshift",
    "splice_site",
    "synonymous",
}


def filter_protein_coding_variants(annotated_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to protein-coding consequence classes.

    Parameters
    ----------
    annotated_df : pd.DataFrame
        Annotated variant table.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame.
    """
    return annotated_df[annotated_df["consequence"].isin(PROTEIN_CODING_CONSEQUENCES)].copy()


def filter_high_impact_variants(annotated_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to high-impact variant consequence classes.

    Parameters
    ----------
    annotated_df : pd.DataFrame
        Annotated variant table.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame.
    """
    return annotated_df[annotated_df["consequence"].isin(HIGH_IMPACT_CONSEQUENCES)].copy()


def filter_annotated_variants(annotated_df: pd.DataFrame) -> pd.DataFrame:
    """
    Retain variants with assigned annotation data.

    Parameters
    ----------
    annotated_df : pd.DataFrame
        Annotated variant table.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame.
    """
    return annotated_df[annotated_df["gene_symbol"] != "UNKNOWN"].copy()


def apply_filters(annotated_df: pd.DataFrame, config: dict[str, Any], logger) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Apply configured filtering logic to the annotated variants.

    Parameters
    ----------
    annotated_df : pd.DataFrame
        Annotated variant table.
    config : dict[str, Any]
        Parsed pipeline configuration.
    logger : logging.Logger
        Configured pipeline logger.

    Returns
    -------
    tuple[pd.DataFrame, dict[str, int]]
        Filtered DataFrame and summary counts after each filter step.
    """
    filtered_df = annotated_df.copy()
    counts = {
        "starting_row_count": len(filtered_df),
    }

    if config["filtering"]["protein_coding_only"]:
        logger.info("Applying protein-coding consequence filter.")
        filtered_df = filter_protein_coding_variants(filtered_df)
    counts["after_protein_coding_filter"] = len(filtered_df)

    if config["filtering"]["high_impact_only"]:
        logger.info("Applying high-impact consequence filter.")
        filtered_df = filter_high_impact_variants(filtered_df)
    counts["after_high_impact_filter"] = len(filtered_df)

    if config["filtering"]["require_annotation"]:
        logger.info("Requiring assigned annotation data.")
        filtered_df = filter_annotated_variants(filtered_df)
    counts["after_annotation_filter"] = len(filtered_df)

    allowed_consequences = config["filtering"]["allowed_consequences"]
    logger.info(f"Restricting to allowed consequences: {allowed_consequences}")
    filtered_df = filtered_df[filtered_df["consequence"].isin(allowed_consequences)].copy()
    counts["after_allowed_consequence_filter"] = len(filtered_df)

    return filtered_df, counts


def prioritize_variants(filtered_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply a simple prioritization ranking to filtered variants.

    Priority order:
    1. pathogenic
    2. likely_pathogenic
    3. uncertain_significance
    4. likely_benign
    5. unclassified

    Parameters
    ----------
    filtered_df : pd.DataFrame
        Filtered annotated variant table.

    Returns
    -------
    pd.DataFrame
        Prioritized DataFrame sorted by clinical annotation and position.
    """
    prioritized_df = filtered_df.copy()

    priority_map = {
        "pathogenic": 1,
        "likely_pathogenic": 2,
        "uncertain_significance": 3,
        "likely_benign": 4,
        "unclassified": 5,
    }

    prioritized_df["priority_rank"] = prioritized_df["clinical_annotation"].map(priority_map).fillna(99).astype(int)

    prioritized_df = prioritized_df.sort_values(
        by=["priority_rank", "gene_symbol", "chromosome", "position"],
        ascending=[True, True, True, True],
    ).reset_index(drop=True)

    return prioritized_df


def write_final_output(
    prioritized_df: pd.DataFrame,
    paths: dict[str, Path],
    config: dict[str, Any],
) -> Path:
    """
    Write prioritized variants to the run-specific final output directory.

    Parameters
    ----------
    prioritized_df : pd.DataFrame
        Prioritized variant table.
    paths : dict[str, Path]
        Resolved pipeline paths.
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    Path
        Path to the written final TSV file.
    """
    output_filename = config["outputs"]["final_filename"]
    output_path = paths["run_final_dir"] / output_filename
    prioritized_df.to_csv(output_path, sep="\t", index=False)
    return output_path


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 05: filter and prioritize annotated variants.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    paths : dict[str, Path]
        Resolved run-specific paths.
    logger : logging.Logger
        Configured pipeline logger.
    state : dict[str, Any]
        Shared pipeline state.

    Returns
    -------
    dict[str, Any]
        Updated pipeline state.

    Raises
    ------
    ValueError
        If annotated input data is not available.
    """
    logger.info("Stage 05: filtering and prioritizing annotated variants.")

    if "annotated_variants_df" not in state:
        raise ValueError("Stage 05 expected 'annotated_variants_df' in state, but it was not found.")

    annotated_df = state["annotated_variants_df"]
    if not isinstance(annotated_df, pd.DataFrame):
        raise ValueError("Stage 05 expected 'annotated_variants_df' to be a pandas DataFrame.")

    filtered_df, filter_counts = apply_filters(annotated_df, config, logger)
    prioritized_df = prioritize_variants(filtered_df)

    write_final_table = config["outputs"]["write_final_table"]
    output_path = None
    if write_final_table:
        output_path = write_final_output(prioritized_df, paths, config)
        logger.info(f"Final prioritized variant table written to: {output_path}")

    final_row_count = len(prioritized_df)
    prioritized_gene_count = int(prioritized_df["gene_symbol"].nunique()) if not prioritized_df.empty else 0

    logger.info(f"Final prioritized row count: {final_row_count}")
    logger.info(f"Number of prioritized genes: {prioritized_gene_count}")

    state["prioritized_variants_df"] = prioritized_df
    state["stage_outputs"]["analyze_data"] = {
        "filter_counts": filter_counts,
        "final_row_count": final_row_count,
        "prioritized_gene_count": prioritized_gene_count,
        "final_output_path": str(output_path) if output_path else None,
    }

    return state


if __name__ == "__main__":
    import logging

    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
    from pipeline.stage_02_validate_data import run_stage as run_stage_02_validate_data
    from pipeline.stage_03_clean_data import run_stage as run_stage_03_clean_data
    from pipeline.stage_04_transform_data import run_stage as run_stage_04_transform_data
    from src.config_loader import get_input_vcf_path, load_config, validate_config_paths
    from src.path_manager import initialize_run_paths

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_05_test")

    test_config = load_config("config/config.yaml")
    validate_config_paths(test_config)
    test_paths = initialize_run_paths(test_config)

    test_state = {
        "input_vcf_path": get_input_vcf_path(test_config),
        "stage_outputs": {},
    }

    test_state = run_stage_01_load_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_02_validate_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_03_clean_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_04_transform_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 05 completed successfully.")
    print(test_state["stage_outputs"]["analyze_data"])