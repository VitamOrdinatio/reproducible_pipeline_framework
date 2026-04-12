"""
Stage 01: Load variant data from a VCF file.

Version 1 responsibilities:
- select the active input VCF path from state
- confirm the file exists
- parse a minimal VCF structure
- convert records into a pandas DataFrame
- store the DataFrame in state
- record basic stage outputs and counts
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


VCF_COLUMNS = [
    "chromosome",
    "position",
    "variant_id",
    "reference_allele",
    "alternate_allele",
    "quality",
    "filter",
    "info",
]


def parse_vcf(vcf_path: Path) -> pd.DataFrame:
    """
    Parse a minimal VCF file into a pandas DataFrame.

    Parameters
    ----------
    vcf_path : Path
        Path to the input VCF file.

    Returns
    -------
    pd.DataFrame
        Parsed variant records.

    Raises
    ------
    ValueError
        If no variant records are found or rows are malformed.
    """
    records: list[list[Any]] = []

    with vcf_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()

            if not line:
                continue

            if line.startswith("##"):
                continue

            if line.startswith("#CHROM"):
                continue

            fields = line.split("\t")
            if len(fields) < 8:
                raise ValueError(f"Malformed VCF row with fewer than 8 columns: {line}")

            record = [
                fields[0],
                int(fields[1]),
                fields[2],
                fields[3],
                fields[4],
                fields[5],
                fields[6],
                fields[7],
            ]
            records.append(record)

    if not records:
        raise ValueError(f"No variant records found in VCF: {vcf_path}")

    dataframe = pd.DataFrame(records, columns=VCF_COLUMNS)
    return dataframe


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 01: load variant data.

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
    FileNotFoundError
        If the selected input VCF does not exist.
    ValueError
        If the VCF cannot be parsed or contains no records.
    """
    input_vcf_path = Path(state["input_vcf_path"])

    logger.info("Stage 01: loading variant data.")
    logger.info(f"Input VCF path: {input_vcf_path}")

    if not input_vcf_path.exists():
        raise FileNotFoundError(f"Input VCF file not found: {input_vcf_path}")

    if not input_vcf_path.is_file():
        raise ValueError(f"Input VCF path is not a file: {input_vcf_path}")

    variants_df = parse_vcf(input_vcf_path)

    row_count = len(variants_df)
    column_count = len(variants_df.columns)

    logger.info(f"Loaded {row_count} variant records.")
    logger.info(f"Detected {column_count} columns.")

    state["raw_variants_df"] = variants_df
    state["stage_outputs"]["load_data"] = {
        "input_vcf_path": str(input_vcf_path),
        "row_count": row_count,
        "column_count": column_count,
        "columns": list(variants_df.columns),
    }

    return state


if __name__ == "__main__":
    import logging

    from src.config_loader import get_input_vcf_path, load_config, validate_config_paths
    from src.path_manager import initialize_run_paths

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_01_test")

    test_config = load_config("config/config.yaml")
    validate_config_paths(test_config)
    test_paths = initialize_run_paths(test_config)

    test_state = {
        "input_vcf_path": get_input_vcf_path(test_config),
        "stage_outputs": {},
    }

    updated_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 01 completed successfully.")
    print(updated_state["stage_outputs"]["load_data"])