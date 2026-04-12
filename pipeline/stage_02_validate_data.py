"""
Stage 02: Validate loaded variant data.

Version 1 responsibilities:
- confirm that Stage 01 produced a DataFrame
- validate required columns from config
- check for critical missing values if disallowed
- record validation results in state
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def validate_required_columns(variants_df: pd.DataFrame, required_columns: list[str]) -> None:
    """
    Ensure all required columns are present in the DataFrame.

    Parameters
    ----------
    variants_df : pd.DataFrame
        Variant table loaded from the input VCF.
    required_columns : list[str]
        Columns required by pipeline configuration.

    Raises
    ------
    ValueError
        If one or more required columns are missing.
    """
    missing_columns = [column for column in required_columns if column not in variants_df.columns]
    if missing_columns:
        missing_str = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns: {missing_str}")


def validate_missing_values(variants_df: pd.DataFrame, required_columns: list[str], allow_missing_values: bool) -> dict[str, int]:
    """
    Check missing values across required columns.

    Parameters
    ----------
    variants_df : pd.DataFrame
        Variant table to validate.
    required_columns : list[str]
        Columns considered critical for validation.
    allow_missing_values : bool
        Whether missing values are allowed.

    Returns
    -------
    dict[str, int]
        Mapping of column name to missing-value count for required columns.

    Raises
    ------
    ValueError
        If missing values are present in required columns and not allowed.
    """
    missing_counts = {
        column: int(variants_df[column].isna().sum())
        for column in required_columns
    }

    total_missing = sum(missing_counts.values())
    if total_missing > 0 and not allow_missing_values:
        nonzero_columns = {column: count for column, count in missing_counts.items() if count > 0}
        raise ValueError(f"Missing values detected in required columns: {nonzero_columns}")

    return missing_counts


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 02: validate variant data.

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
        If required columns are missing, data is absent, or validation fails.
    """
    logger.info("Stage 02: validating variant data.")

    if "raw_variants_df" not in state:
        raise ValueError("Stage 02 expected 'raw_variants_df' in state, but it was not found.")

    variants_df = state["raw_variants_df"]
    if not isinstance(variants_df, pd.DataFrame):
        raise ValueError("Stage 02 expected 'raw_variants_df' to be a pandas DataFrame.")

    required_columns = config["validation"]["required_columns"]
    allow_missing_values = config["validation"]["allow_missing_values"]

    validate_required_columns(variants_df, required_columns)
    missing_counts = validate_missing_values(variants_df, required_columns, allow_missing_values)

    row_count = len(variants_df)
    column_count = len(variants_df.columns)

    logger.info(f"Validation passed for {row_count} records across {column_count} columns.")
    logger.info(f"Required columns present: {required_columns}")
    logger.info(f"Missing value counts in required columns: {missing_counts}")

    state["stage_outputs"]["validate_data"] = {
        "row_count": row_count,
        "column_count": column_count,
        "required_columns": required_columns,
        "missing_value_counts": missing_counts,
        "validation_status": "passed",
    }

    return state


if __name__ == "__main__":
    import logging

    from src.config_loader import get_input_vcf_path, load_config, validate_config_paths
    from src.path_manager import initialize_run_paths
    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_02_test")

    test_config = load_config("config/config.yaml")
    validate_config_paths(test_config)
    test_paths = initialize_run_paths(test_config)

    test_state = {
        "input_vcf_path": get_input_vcf_path(test_config),
        "stage_outputs": {},
    }

    test_state = run_stage_01_load_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 02 completed successfully.")
    print(test_state["stage_outputs"]["validate_data"])