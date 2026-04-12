"""
Stage 04: Transform cleaned variant data into an annotated demonstration table.

Version 1 responsibilities:
- confirm that Stage 03 produced a cleaned DataFrame
- add placeholder annotation columns
- write annotated output to data/processed/
- store annotated DataFrame in state
- record transformation summary in state

This stage uses simplified annotation logic for demonstration purposes.
It is intended to make the pipeline runnable and structurally realistic,
not biologically comprehensive.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


GENE_SYMBOL_MAP = {
    ("chr1", 123456): "POLG",
    ("chr1", 123789): "TWNK",
    ("chr2", 555000): "TFAM",
    ("chr2", 987654): "POLRMT",
    ("chrX", 111111): "LIG3",
}


CONSEQUENCE_MAP = {
    "A>G": "missense",
    "C>T": "nonsense",
    "G>A": "synonymous",
    "T>C": "splice_site",
    "G>T": "frameshift",
}


CLINICAL_ANNOTATION_MAP = {
    "missense": "uncertain_significance",
    "nonsense": "likely_pathogenic",
    "synonymous": "likely_benign",
    "splice_site": "pathogenic",
    "frameshift": "pathogenic",
}


def build_variant_key(row: pd.Series) -> str:
    """
    Build a simple REF>ALT key for consequence assignment.

    Parameters
    ----------
    row : pd.Series
        Variant record.

    Returns
    -------
    str
        Variant key such as A>G.
    """
    return f"{row['reference_allele']}>{row['alternate_allele']}"


def assign_gene_symbol(row: pd.Series) -> str:
    """
    Assign a placeholder gene symbol using chromosome and position.

    Parameters
    ----------
    row : pd.Series
        Variant record.

    Returns
    -------
    str
        Gene symbol or 'UNKNOWN'.
    """
    key = (row["chromosome"], int(row["position"]))
    return GENE_SYMBOL_MAP.get(key, "UNKNOWN")


def assign_consequence(row: pd.Series) -> str:
    """
    Assign a placeholder variant consequence using REF>ALT pattern.

    Parameters
    ----------
    row : pd.Series
        Variant record.

    Returns
    -------
    str
        Consequence label.
    """
    variant_key = build_variant_key(row)
    return CONSEQUENCE_MAP.get(variant_key, "other")


def assign_clinical_annotation(consequence: str) -> str:
    """
    Assign a placeholder clinical annotation from consequence.

    Parameters
    ----------
    consequence : str
        Variant consequence.

    Returns
    -------
    str
        Clinical annotation label.
    """
    return CLINICAL_ANNOTATION_MAP.get(consequence, "unclassified")


def annotate_variants(cleaned_df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """
    Add placeholder annotation columns to the cleaned variant table.

    Parameters
    ----------
    cleaned_df : pd.DataFrame
        Cleaned variant table from Stage 03.
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    pd.DataFrame
        Annotated variant table.
    """
    annotated_df = cleaned_df.copy()

    if config["annotation"]["add_gene_symbol"]:
        annotated_df["gene_symbol"] = annotated_df.apply(assign_gene_symbol, axis=1)

    if config["annotation"]["add_consequence"]:
        annotated_df["consequence"] = annotated_df.apply(assign_consequence, axis=1)
    else:
        annotated_df["consequence"] = "unassigned"

    if config["annotation"]["add_clinical_annotation"]:
        annotated_df["clinical_annotation"] = annotated_df["consequence"].apply(assign_clinical_annotation)

    return annotated_df


def write_processed_output(
    annotated_df: pd.DataFrame,
    paths: dict[str, Path],
    config: dict[str, Any],
) -> Path:
    """
    Write annotated variants to the processed data directory.

    Parameters
    ----------
    annotated_df : pd.DataFrame
        Annotated variant table.
    paths : dict[str, Path]
        Resolved pipeline paths.
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    Path
        Path to the written processed TSV file.
    """
    output_filename = config["outputs"]["processed_filename"]
    output_path = paths["processed_dir"] / output_filename
    annotated_df.to_csv(output_path, sep="\t", index=False)
    return output_path


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 04: transform cleaned variant data into annotated form.

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
        If cleaned input data is not available.
    """
    logger.info("Stage 04: transforming and annotating variant data.")

    if "cleaned_variants_df" not in state:
        raise ValueError("Stage 04 expected 'cleaned_variants_df' in state, but it was not found.")

    cleaned_df = state["cleaned_variants_df"]
    if not isinstance(cleaned_df, pd.DataFrame):
        raise ValueError("Stage 04 expected 'cleaned_variants_df' to be a pandas DataFrame.")

    annotated_df = annotate_variants(cleaned_df, config)

    write_processed_table = config["outputs"]["write_processed_table"]
    output_path = None
    if write_processed_table:
        output_path = write_processed_output(annotated_df, paths, config)
        logger.info(f"Processed annotated table written to: {output_path}")

    row_count = len(annotated_df)
    column_count = len(annotated_df.columns)
    annotated_columns = list(annotated_df.columns)

    gene_symbol_count = int((annotated_df["gene_symbol"] != "UNKNOWN").sum()) if "gene_symbol" in annotated_df.columns else 0
    consequence_count = int(annotated_df["consequence"].notna().sum()) if "consequence" in annotated_df.columns else 0

    logger.info(f"Annotated row count: {row_count}")
    logger.info(f"Annotated column count: {column_count}")
    logger.info(f"Variants with assigned gene symbols: {gene_symbol_count}")
    logger.info(f"Variants with assigned consequences: {consequence_count}")

    state["annotated_variants_df"] = annotated_df
    state["stage_outputs"]["transform_data"] = {
        "row_count": row_count,
        "column_count": column_count,
        "annotated_columns": annotated_columns,
        "gene_symbol_count": gene_symbol_count,
        "consequence_count": consequence_count,
        "processed_output_path": str(output_path) if output_path else None,
        "annotation_source": config["annotation"]["annotation_source"],
    }

    return state


if __name__ == "__main__":
    import logging

    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
    from pipeline.stage_02_validate_data import run_stage as run_stage_02_validate_data
    from pipeline.stage_03_clean_data import run_stage as run_stage_03_clean_data
    from src.config_loader import get_input_vcf_path, load_config, validate_config_paths
    from src.path_manager import initialize_run_paths

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_04_test")

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
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 04 completed successfully.")
    print(test_state["stage_outputs"]["transform_data"])