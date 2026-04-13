"""
Stage 08: Filter annotated variants and partition into coding and non-coding tracks.

Version 2 responsibilities:
- read the annotated variant table from Stage 07
- apply lightweight global filtering using allele-frequency thresholds
- partition retained variants into:
  - coding track
  - non-coding track
- write filtered and track-specific output tables
- update artifacts, track summaries, QC, and stage_outputs in state

This stage uses simplified framework-safe logic and does not attempt
production-grade clinical filtering. Its purpose is to preserve:
- stage boundaries
- artifact creation
- state transitions
- reproducibility
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def validate_annotated_table(state: dict[str, Any]) -> Path:
    """
    Validate the annotated table artifact from Stage 07.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    Path
        Path to the annotated table.

    Raises
    ------
    ValueError
        If the annotated table path is missing.
    FileNotFoundError
        If the annotated table file does not exist.
    """
    annotated_table = state["artifacts"].get("annotated_table")
    if not annotated_table:
        raise ValueError("Stage 08 requires artifacts.annotated_table.")

    annotated_table_path = Path(annotated_table)
    if not annotated_table_path.exists():
        raise FileNotFoundError(f"Annotated table not found: {annotated_table_path}")

    return annotated_table_path


def load_annotated_table(annotated_table_path: Path) -> pd.DataFrame:
    """
    Load the annotated TSV into a DataFrame.

    Parameters
    ----------
    annotated_table_path : Path
        Path to the annotated TSV.

    Returns
    -------
    pd.DataFrame
        Annotated variants DataFrame.
    """
    return pd.read_csv(annotated_table_path, sep="\t")


def apply_global_filters(df: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Apply simplified global filtering using allele frequency thresholds.

    Parameters
    ----------
    df : pd.DataFrame
        Annotated variants DataFrame.
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    tuple[pd.DataFrame, dict[str, Any]]
        Filtered DataFrame and filtering summary.
    """
    apply_af_filtering = bool(config["filtering"]["apply_af_filtering"])
    require_annotation = bool(config["filtering"]["require_annotation"])
    coding_af_threshold = float(config["filtering"]["coding_af_threshold"])
    noncoding_af_threshold = float(config["filtering"]["noncoding_af_threshold"])

    original_count = len(df)
    filtered_df = df.copy()

    if require_annotation:
        filtered_df = filtered_df[filtered_df["gene_symbol"].notna()].copy()

    if apply_af_filtering:
        coding_mask = filtered_df["variant_type"] == "coding"
        noncoding_mask = filtered_df["variant_type"] == "non-coding"

        coding_keep = (~coding_mask) | (filtered_df["af_gnomad"] <= coding_af_threshold)
        noncoding_keep = (~noncoding_mask) | (filtered_df["af_gnomad"] <= noncoding_af_threshold)

        filtered_df = filtered_df[coding_keep & noncoding_keep].copy()

    filtered_count = len(filtered_df)

    summary = {
        "original_count": original_count,
        "filtered_count": filtered_count,
        "variants_removed": original_count - filtered_count,
        "apply_af_filtering": apply_af_filtering,
        "require_annotation": require_annotation,
        "coding_af_threshold": coding_af_threshold,
        "noncoding_af_threshold": noncoding_af_threshold,
    }

    return filtered_df, summary


def partition_tracks(filtered_df: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Partition filtered variants into coding and non-coding tracks.

    Parameters
    ----------
    filtered_df : pd.DataFrame
        Filtered variant table.
    config : dict[str, Any]
        Parsed pipeline configuration.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Coding-track DataFrame and non-coding-track DataFrame.
    """
    coding_consequences = set(config["filtering"]["coding_consequences"])
    noncoding_consequences = set(config["filtering"]["noncoding_consequences"])

    coding_df = filtered_df[filtered_df["consequence"].isin(coding_consequences)].copy()
    noncoding_df = filtered_df[filtered_df["consequence"].isin(noncoding_consequences)].copy()

    return coding_df, noncoding_df


def write_track_outputs(
    filtered_df: pd.DataFrame,
    coding_df: pd.DataFrame,
    noncoding_df: pd.DataFrame,
    paths: dict[str, Path | str],
) -> dict[str, str]:
    """
    Write filtered and track-specific output tables.

    Parameters
    ----------
    filtered_df : pd.DataFrame
        Globally filtered variants.
    coding_df : pd.DataFrame
        Coding-track variants.
    noncoding_df : pd.DataFrame
        Non-coding-track variants.
    paths : dict[str, Path | str]
        Resolved pipeline paths.

    Returns
    -------
    dict[str, str]
        Written output paths as strings.
    """
    run_final_dir = Path(paths["run_final_dir"])
    filtered_table_path = run_final_dir / "filtered_variants.tsv"
    coding_table_path = Path(paths["coding_track_table"])
    noncoding_table_path = Path(paths["noncoding_track_table"])

    filtered_df.to_csv(filtered_table_path, sep="\t", index=False)
    coding_df.to_csv(coding_table_path, sep="\t", index=False)
    noncoding_df.to_csv(noncoding_table_path, sep="\t", index=False)

    return {
        "filtered_variants": str(filtered_table_path),
        "coding_track_table": str(coding_table_path),
        "noncoding_track_table": str(noncoding_table_path),
    }


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 08: filter and partition annotated variants.

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
    logger.info("Stage 08: filtering and partitioning annotated variants.")

    annotated_table_path = validate_annotated_table(state)
    annotated_df = load_annotated_table(annotated_table_path)

    filtered_df, filtering_summary = apply_global_filters(annotated_df, config)
    coding_df, noncoding_df = partition_tracks(filtered_df, config)
    written_paths = write_track_outputs(filtered_df, coding_df, noncoding_df, paths)

    filtered_count = len(filtered_df)
    coding_count = len(coding_df)
    noncoding_count = len(noncoding_df)

    state["artifacts"]["filtered_variants"] = written_paths["filtered_variants"]
    state["artifacts"]["coding_track_table"] = written_paths["coding_track_table"]
    state["artifacts"]["noncoding_track_table"] = written_paths["noncoding_track_table"]

    state["tracks"]["coding"] = {
        "table_path": written_paths["coding_track_table"],
        "variant_count": coding_count,
    }
    state["tracks"]["noncoding"] = {
        "table_path": written_paths["noncoding_track_table"],
        "variant_count": noncoding_count,
    }

    state["qc"]["filtering_qc"] = {
        **filtering_summary,
        "coding_count": coding_count,
        "noncoding_count": noncoding_count,
    }

    state["stage_outputs"]["stage_08_filter_and_partition"] = {
        "status": "success",
        "annotated_table": str(annotated_table_path),
        "filtered_variants": written_paths["filtered_variants"],
        "coding_track_table": written_paths["coding_track_table"],
        "noncoding_track_table": written_paths["noncoding_track_table"],
        "filtered_count": filtered_count,
        "coding_count": coding_count,
        "noncoding_count": noncoding_count,
    }

    logger.info(f"Filtered variants written to: {written_paths['filtered_variants']}")
    logger.info(f"Coding track written to: {written_paths['coding_track_table']}")
    logger.info(f"Non-coding track written to: {written_paths['noncoding_track_table']}")
    logger.info(f"Filtered count: {filtered_count}")
    logger.info(f"Coding count: {coding_count}")
    logger.info(f"Non-coding count: {noncoding_count}")

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
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_08_test")

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
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 08 completed successfully.")
    print(test_state["stage_outputs"]["stage_08_filter_and_partition"])