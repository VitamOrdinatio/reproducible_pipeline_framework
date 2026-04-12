"""
Stage 03: Clean and normalize variant data.

Version 1 responsibilities:
- confirm that Stage 02 validation has completed
- normalize chromosome naming if enabled
- drop malformed rows if enabled
- drop duplicate variants if enabled
- write cleaned output to data/interim/
- store cleaned DataFrame in state
- record cleaning summary in state
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def normalize_chromosome_value(value: Any) -> Any:
    """
    Normalize a chromosome label to a canonical 'chr' prefixed form.

    Examples
    --------
    1 -> chr1
    chr1 -> chr1
    X -> chrX
    MT -> chrMT
    """
    if pd.isna(value):
        return value

    chromosome = str(value).strip()
    if not chromosome:
        return chromosome

    if chromosome.lower().startswith("chr"):
        suffix = chromosome[3:]
        return f"chr{suffix}"

    return f"chr{chromosome}"


def normalize_chromosome_column(variants_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize chromosome labels in the chromosome column.

    Parameters
    ----------
    variants_df : pd.DataFrame
        Input variant table.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized chromosome values.
    """
    cleaned_df = variants_df.copy()
    cleaned_df["chromosome"] = cleaned_df["chromosome"].apply(normalize_chromosome_value)
    return cleaned_df


def drop_malformed_rows(variants_df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Drop rows missing critical variant fields.

    Critical fields:
    - chromosome
    - position
    - reference_allele
    - alternate_allele

    Parameters
    ----------
    variants_df : pd.DataFrame
        Input variant table.

    Returns
    -------
    tuple[pd.DataFrame, int]
        Cleaned DataFrame and number of dropped rows.
    """
    required_fields = [
        "chromosome",
        "position",
        "reference_allele",
        "alternate_allele",
    ]

    original_row_count = len(variants_df)
    cleaned_df = variants_df.dropna(subset=required_fields).copy()
    dropped_row_count = original_row_count - len(cleaned_df)

    return cleaned_df, dropped_row_count


def drop_duplicate_variants(variants_df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Drop duplicate variants based on core identifying fields.

    Duplicate identity is defined by:
    - chromosome
    - position
    - reference_allele
    - alternate_allele

    Parameters
    ----------
    variants_df : pd.DataFrame
        Input variant table.

    Returns
    -------
    tuple[pd.DataFrame, int]
        Deduplicated DataFrame and number of dropped rows.
    """
    duplicate_subset = [
        "chromosome",
        "position",
        "reference_allele",
        "alternate_allele",
    ]

    original_row_count = len(variants_df)
    cleaned_df = variants_df.drop_duplicates(subset=duplicate_subset).copy()
    dropped_row_count = original_row_count - len(cleaned_df)

    return cleaned_df, dropped_row_count


def write_cleaned_output(
    cleaned_df: pd.DataFrame,
    paths: dict[str, Path],
    config: dict[str, Any],
) -> Path:
    """
    Write cleaned variants to the interim data directory.

    Parameters
    ----------
    cleaned_df : pd.DataFrame
        Cleaned variant table.
    paths : dict[str, Path]
        Resolved pipeline paths.
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    Path
        Path to the written interim TSV file.
    """
    output_filename = config["outputs"]["interim_filename"]
    output_path = paths["interim_dir"] / output_filename
    cleaned_df.to_csv(output_path, sep="\t", index=False)
    return output_path


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 03: clean and normalize variant data.

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
        If validated input data is not available.
    """
    logger.info("Stage 03: cleaning and normalizing variant data.")

    if "raw_variants_df" not in state:
        raise ValueError("Stage 03 expected 'raw_variants_df' in state, but it was not found.")

    variants_df = state["raw_variants_df"]
    if not isinstance(variants_df, pd.DataFrame):
        raise ValueError("Stage 03 expected 'raw_variants_df' to be a pandas DataFrame.")

    cleaned_df = variants_df.copy()
    original_row_count = len(cleaned_df)

    normalize_prefix = config["cleaning"]["normalize_chromosome_prefix"]
    drop_malformed = config["cleaning"]["drop_malformed_rows"]
    drop_duplicates = config["cleaning"]["drop_duplicate_variants"]
    write_interim_table = config["outputs"]["write_interim_table"]

    malformed_rows_dropped = 0
    duplicate_rows_dropped = 0

    if normalize_prefix:
        logger.info("Normalizing chromosome labels.")
        cleaned_df = normalize_chromosome_column(cleaned_df)

    if drop_malformed:
        logger.info("Dropping malformed rows.")
        cleaned_df, malformed_rows_dropped = drop_malformed_rows(cleaned_df)

    if drop_duplicates:
        logger.info("Dropping duplicate variants.")
        cleaned_df, duplicate_rows_dropped = drop_duplicate_variants(cleaned_df)

    final_row_count = len(cleaned_df)
    total_rows_removed = original_row_count - final_row_count

    output_path = None
    if write_interim_table:
        output_path = write_cleaned_output(cleaned_df, paths, config)
        logger.info(f"Cleaned interim table written to: {output_path}")

    logger.info(f"Original row count: {original_row_count}")
    logger.info(f"Final row count after cleaning: {final_row_count}")
    logger.info(f"Malformed rows dropped: {malformed_rows_dropped}")
    logger.info(f"Duplicate rows dropped: {duplicate_rows_dropped}")
    logger.info(f"Total rows removed: {total_rows_removed}")

    state["cleaned_variants_df"] = cleaned_df
    state["stage_outputs"]["clean_data"] = {
        "original_row_count": original_row_count,
        "final_row_count": final_row_count,
        "malformed_rows_dropped": malformed_rows_dropped,
        "duplicate_rows_dropped": duplicate_rows_dropped,
        "total_rows_removed": total_rows_removed,
        "chromosome_normalization_applied": normalize_prefix,
        "interim_output_path": str(output_path) if output_path else None,
    }

    return state


if __name__ == "__main__":
    import logging

    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
    from pipeline.stage_02_validate_data import run_stage as run_stage_02_validate_data
    from src.config_loader import get_input_vcf_path, load_config, validate_config_paths
    from src.path_manager import initialize_run_paths

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_03_test")

    test_config = load_config("config/config.yaml")
    validate_config_paths(test_config)
    test_paths = initialize_run_paths(test_config)

    test_state = {
        "input_vcf_path": get_input_vcf_path(test_config),
        "stage_outputs": {},
    }

    test_state = run_stage_01_load_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_02_validate_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 03 completed successfully.")
    print(test_state["stage_outputs"]["clean_data"])