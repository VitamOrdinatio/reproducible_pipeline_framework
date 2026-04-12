"""
Stage 06: Write final summary outputs for the pipeline run.

Version 1 responsibilities:
- confirm that Stage 05 produced a prioritized DataFrame
- generate a concise human-readable summary report
- optionally write summary tables into the run reports directory
- record reporting summary in state

This stage is intentionally simple for Version 1.
It provides a clean demonstration of final reporting behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def build_summary_lines(
    config: dict[str, Any],
    paths: dict[str, Path],
    state: dict[str, Any],
    prioritized_df: pd.DataFrame,
) -> list[str]:
    """
    Build a human-readable summary report as a list of lines.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    paths : dict[str, Path]
        Resolved run-specific paths.
    state : dict[str, Any]
        Shared pipeline state.
    prioritized_df : pd.DataFrame
        Final prioritized variant table.

    Returns
    -------
    list[str]
        Summary report lines.
    """
    project_name = config["project"]["name"]
    pipeline_name = config["project"]["pipeline_name"]
    pipeline_version = config["project"]["version"]
    run_id = paths["run_id"].name
    input_vcf_path = state["input_vcf_path"]

    raw_row_count = state["stage_outputs"].get("load_data", {}).get("row_count", "NA")
    cleaned_row_count = state["stage_outputs"].get("clean_data", {}).get("final_row_count", "NA")
    final_row_count = state["stage_outputs"].get("analyze_data", {}).get("final_row_count", "NA")

    prioritized_gene_count = int(prioritized_df["gene_symbol"].nunique()) if not prioritized_df.empty else 0

    top_genes = []
    if not prioritized_df.empty and "gene_symbol" in prioritized_df.columns:
        top_genes = prioritized_df["gene_symbol"].value_counts().head(5).index.tolist()

    clinical_counts = {}
    if not prioritized_df.empty and "clinical_annotation" in prioritized_df.columns:
        clinical_counts = prioritized_df["clinical_annotation"].value_counts().to_dict()

    consequence_counts = {}
    if not prioritized_df.empty and "consequence" in prioritized_df.columns:
        consequence_counts = prioritized_df["consequence"].value_counts().to_dict()

    lines = [
        "Pipeline Summary Report",
        "=======================",
        "",
        f"Project name: {project_name}",
        f"Pipeline name: {pipeline_name}",
        f"Pipeline version: {pipeline_version}",
        f"Run ID: {run_id}",
        f"Input VCF: {input_vcf_path}",
        "",
        "Row counts",
        "----------",
        f"Raw variants loaded: {raw_row_count}",
        f"Variants after cleaning: {cleaned_row_count}",
        f"Final prioritized variants: {final_row_count}",
        f"Unique prioritized genes: {prioritized_gene_count}",
        "",
        "Top prioritized genes",
        "---------------------",
    ]

    if top_genes:
        lines.extend([f"- {gene}" for gene in top_genes])
    else:
        lines.append("No prioritized genes identified.")

    lines.extend([
        "",
        "Clinical annotation counts",
        "--------------------------",
    ])

    if clinical_counts:
        lines.extend([f"- {label}: {count}" for label, count in clinical_counts.items()])
    else:
        lines.append("No clinical annotation counts available.")

    lines.extend([
        "",
        "Consequence counts",
        "------------------",
    ])

    if consequence_counts:
        lines.extend([f"- {label}: {count}" for label, count in consequence_counts.items()])
    else:
        lines.append("No consequence counts available.")

    lines.extend([
        "",
        "Output locations",
        "----------------",
        f"Run directory: {paths['run_dir']}",
        f"Final variants: {state['stage_outputs'].get('analyze_data', {}).get('final_output_path', 'NA')}",
        f"Metadata file: {paths['metadata_file']}",
        f"Log file: {paths['log_file']}",
    ])

    return lines


def write_summary_report(
    report_lines: list[str],
    paths: dict[str, Path],
    config: dict[str, Any],
) -> Path:
    """
    Write the human-readable summary report to disk.

    Parameters
    ----------
    report_lines : list[str]
        Summary report lines.
    paths : dict[str, Path]
        Resolved pipeline paths.
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    Path
        Path to the written report file.
    """
    report_filename = config["outputs"]["summary_report_filename"]
    report_path = paths["run_reports_dir"] / report_filename

    with report_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(report_lines) + "\n")

    return report_path


def write_summary_table(prioritized_df: pd.DataFrame, paths: dict[str, Path]) -> Path:
    """
    Write a compact summary table of final prioritized variants.

    Parameters
    ----------
    prioritized_df : pd.DataFrame
        Final prioritized variant table.
    paths : dict[str, Path]
        Resolved pipeline paths.

    Returns
    -------
    Path
        Path to the written summary TSV file.
    """
    summary_table_path = paths["run_reports_dir"] / "prioritized_variant_summary.tsv"

    columns_to_keep = [
        column
        for column in [
            "chromosome",
            "position",
            "reference_allele",
            "alternate_allele",
            "gene_symbol",
            "consequence",
            "clinical_annotation",
            "priority_rank",
        ]
        if column in prioritized_df.columns
    ]

    summary_df = prioritized_df[columns_to_keep].copy()
    summary_df.to_csv(summary_table_path, sep="\t", index=False)

    return summary_table_path


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 06: write summary outputs.

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
        If prioritized data is not available.
    """
    logger.info("Stage 06: writing summary outputs.")

    if "prioritized_variants_df" not in state:
        raise ValueError("Stage 06 expected 'prioritized_variants_df' in state, but it was not found.")

    prioritized_df = state["prioritized_variants_df"]
    if not isinstance(prioritized_df, pd.DataFrame):
        raise ValueError("Stage 06 expected 'prioritized_variants_df' to be a pandas DataFrame.")

    summary_lines = build_summary_lines(config, paths, state, prioritized_df)
    report_path = None
    summary_table_path = None

    if config["outputs"]["write_summary_report"]:
        report_path = write_summary_report(summary_lines, paths, config)
        logger.info(f"Summary report written to: {report_path}")

    summary_table_path = write_summary_table(prioritized_df, paths)
    logger.info(f"Summary table written to: {summary_table_path}")

    state["stage_outputs"]["write_summary"] = {
        "report_path": str(report_path) if report_path else None,
        "summary_table_path": str(summary_table_path) if summary_table_path else None,
        "line_count": len(summary_lines),
        "final_row_count": len(prioritized_df),
    }

    return state


if __name__ == "__main__":
    import logging

    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
    from pipeline.stage_02_validate_data import run_stage as run_stage_02_validate_data
    from pipeline.stage_03_clean_data import run_stage as run_stage_03_clean_data
    from pipeline.stage_04_transform_data import run_stage as run_stage_04_transform_data
    from pipeline.stage_05_analyze_data import run_stage as run_stage_05_analyze_data
    from src.config_loader import get_input_vcf_path, load_config, validate_config_paths
    from src.path_manager import initialize_run_paths

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_06_test")

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
    test_state = run_stage_05_analyze_data(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 06 completed successfully.")
    print(test_state["stage_outputs"]["write_summary"])