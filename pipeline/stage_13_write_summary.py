"""
Stage 13: Write final run summary and reporting artifacts.

Version 2 responsibilities:
- aggregate key results from prior stages
- generate a human-readable pipeline summary report
- generate a compact machine-readable run summary table
- confirm major artifacts produced during the run
- update reports and stage_outputs in state

This stage does not perform additional biological analysis.
Its purpose is to produce a clear, reproducible summary of the run.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def collect_artifact_status(state: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Collect artifact existence information from the state object.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    list[dict[str, Any]]
        Artifact status records.
    """
    artifact_records: list[dict[str, Any]] = []

    for artifact_name, artifact_path in state.get("artifacts", {}).items():
        if artifact_path is None:
            artifact_records.append({
                "artifact_name": artifact_name,
                "artifact_path": None,
                "exists": False,
            })
            continue

        path_obj = Path(str(artifact_path))
        artifact_records.append({
            "artifact_name": artifact_name,
            "artifact_path": str(path_obj),
            "exists": path_obj.exists(),
        })

    return artifact_records


def build_summary_lines(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    state: dict[str, Any],
    artifact_records: list[dict[str, Any]],
) -> list[str]:
    """
    Build a human-readable pipeline summary report.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    paths : dict[str, Path | str]
        Resolved pipeline paths.
    state : dict[str, Any]
        Shared nested pipeline state.
    artifact_records : list[dict[str, Any]]
        Artifact status records.

    Returns
    -------
    list[str]
        Summary report lines.
    """
    run_info = state.get("run", {})
    sample_info = state.get("sample", {})
    qc = state.get("qc", {})
    annotations = state.get("annotations", {})
    warnings = state.get("warnings", [])
    errors = state.get("errors", [])
    stage_outputs = state.get("stage_outputs", {})

    prioritization = stage_outputs.get("stage_11_prioritize_variants", {})
    filtering = stage_outputs.get("stage_08_filter_and_partition", {})
    validation = stage_outputs.get("stage_12_validate_variants", {})

    artifact_exists_count = sum(1 for record in artifact_records if record["exists"])
    artifact_total_count = len(artifact_records)

    lines = [
        "Pipeline Summary Report",
        "=======================",
        "",
        f"Project: {config['project']['name']}",
        f"Pipeline: {config['project']['pipeline_name']}",
        f"Version: {config['project']['version']}",
        f"Run ID: {run_info.get('run_id')}",
        f"Execution mode: {run_info.get('mode')}",
        f"Run status: {run_info.get('status')}",
        f"Sample ID: {sample_info.get('sample_id')}",
        f"Reference genome: {sample_info.get('reference_genome')}",
        "",
        "Key Counts",
        "----------",
        f"Annotated variants: {stage_outputs.get('stage_07_annotate_variants', {}).get('annotated_variant_count', 'NA')}",
        f"Filtered variants: {filtering.get('filtered_count', 'NA')}",
        f"Coding variants: {filtering.get('coding_count', 'NA')}",
        f"Non-coding variants: {filtering.get('noncoding_count', 'NA')}",
        f"Prioritized variants: {prioritization.get('variant_count', 'NA')}",
        f"Prioritized genes: {prioritization.get('gene_count', 'NA')}",
        f"Manual IGV review candidates: {validation.get('candidate_count', 'NA')}",
        "",
        "QC Summary",
        "----------",
        f"Input files checked: {len(qc.get('input_qc', {}).get('files_checked', []))}",
        f"Alignment completed: {qc.get('alignment_qc', {}).get('alignment_completed', False)}",
        f"BAM processing completed: {qc.get('bam_processing_qc', {}).get('bam_processing_completed', False)}",
        f"Variant calling completed: {qc.get('variant_calling_qc', {}).get('variant_calling_completed', False)}",
        f"VCF normalization completed: {qc.get('variant_calling_qc', {}).get('vcf_normalization_completed', False)}",
        f"Annotation completed: {qc.get('annotation_qc', {}).get('annotation_completed', False)}",
        f"Validation completed: {qc.get('validation_qc', {}).get('validation_completed', False)}",
        "",
        "Annotation Resources",
        "--------------------",
    ]

    resources_used = annotations.get("resources_used", [])
    if resources_used:
        lines.extend([f"- {resource}" for resource in resources_used])
    else:
        lines.append("- none recorded")

    lines.extend([
        "",
        "Artifacts",
        "---------",
        f"Artifacts present: {artifact_exists_count} / {artifact_total_count}",
    ])

    for record in artifact_records:
        status = "present" if record["exists"] else "missing"
        lines.append(f"- {record['artifact_name']}: {status}")

    lines.extend([
        "",
        "Warnings",
        "--------",
    ])
    if warnings:
        lines.extend([f"- {warning}" for warning in warnings])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "Errors",
        "------",
    ])
    if errors:
        lines.extend([f"- {error}" for error in errors])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "Output Locations",
        "----------------",
        f"Run directory: {paths['run_dir']}",
        f"Reports directory: {paths['run_reports_dir']}",
        f"Validation directory: {paths['run_validation_dir']}",
        f"Final prioritized table: {state['artifacts'].get('prioritized_table')}",
        f"Validation notes: {state['artifacts'].get('validation_notes')}",
        "",
        "End of summary.",
    ])

    return lines


def write_summary_report(report_lines: list[str], summary_report_path: Path) -> None:
    """
    Write the human-readable summary report.

    Parameters
    ----------
    report_lines : list[str]
        Summary report lines.
    summary_report_path : Path
        Destination summary report path.
    """
    with summary_report_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(report_lines) + "\n")


def write_summary_table(
    state: dict[str, Any],
    artifact_records: list[dict[str, Any]],
    summary_table_path: Path,
) -> None:
    """
    Write a compact machine-readable summary table.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.
    artifact_records : list[dict[str, Any]]
        Artifact status records.
    summary_table_path : Path
        Destination summary TSV path.
    """
    stage_outputs = state.get("stage_outputs", {})
    qc = state.get("qc", {})

    rows = [
        {"metric": "run_id", "value": state.get("run", {}).get("run_id")},
        {"metric": "execution_mode", "value": state.get("run", {}).get("mode")},
        {"metric": "run_status", "value": state.get("run", {}).get("status")},
        {"metric": "sample_id", "value": state.get("sample", {}).get("sample_id")},
        {"metric": "annotated_variant_count", "value": stage_outputs.get("stage_07_annotate_variants", {}).get("annotated_variant_count")},
        {"metric": "filtered_variant_count", "value": stage_outputs.get("stage_08_filter_and_partition", {}).get("filtered_count")},
        {"metric": "coding_variant_count", "value": stage_outputs.get("stage_08_filter_and_partition", {}).get("coding_count")},
        {"metric": "noncoding_variant_count", "value": stage_outputs.get("stage_08_filter_and_partition", {}).get("noncoding_count")},
        {"metric": "prioritized_variant_count", "value": stage_outputs.get("stage_11_prioritize_variants", {}).get("variant_count")},
        {"metric": "prioritized_gene_count", "value": stage_outputs.get("stage_11_prioritize_variants", {}).get("gene_count")},
        {"metric": "manual_igv_candidate_count", "value": stage_outputs.get("stage_12_validate_variants", {}).get("candidate_count")},
        {"metric": "artifact_present_count", "value": sum(1 for record in artifact_records if record["exists"])},
        {"metric": "artifact_total_count", "value": len(artifact_records)},
        {"metric": "warning_count", "value": len(state.get("warnings", []))},
        {"metric": "error_count", "value": len(state.get("errors", []))},
        {"metric": "alignment_completed", "value": qc.get("alignment_qc", {}).get("alignment_completed")},
        {"metric": "variant_calling_completed", "value": qc.get("variant_calling_qc", {}).get("variant_calling_completed")},
        {"metric": "annotation_completed", "value": qc.get("annotation_qc", {}).get("annotation_completed")},
        {"metric": "validation_completed", "value": qc.get("validation_qc", {}).get("validation_completed")},
    ]

    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(summary_table_path, sep="\t", index=False)


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 13: write final summary outputs.

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
    logger.info("Stage 13: writing final summary outputs.")

    summary_report_path = Path(paths["summary_report"])
    summary_table_path = Path(paths["summary_table"])

    artifact_records = collect_artifact_status(state)
    report_lines = build_summary_lines(config, paths, state, artifact_records)

    write_summary_report(report_lines, summary_report_path)
    write_summary_table(state, artifact_records, summary_table_path)

    state["reports"] = {
        "summary_report": str(summary_report_path),
        "summary_table": str(summary_table_path),
        "report_line_count": len(report_lines),
    }
    state["artifacts"]["summary_report"] = str(summary_report_path)
    state["stage_outputs"]["stage_13_write_summary"] = {
        "status": "success",
        "summary_report": str(summary_report_path),
        "summary_table": str(summary_table_path),
        "report_line_count": len(report_lines),
        "artifact_present_count": sum(1 for record in artifact_records if record["exists"]),
        "artifact_total_count": len(artifact_records),
    }

    logger.info(f"Summary report written to: {summary_report_path}")
    logger.info(f"Summary table written to: {summary_table_path}")

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
    from pipeline.stage_11_prioritize_variants import run_stage as run_stage_11_prioritize_variants
    from pipeline.stage_12_validate_variants import run_stage as run_stage_12_validate_variants
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_13_test")

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
    test_state = run_stage_11_prioritize_variants(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_12_validate_variants(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 13 completed successfully.")
    print(test_state["stage_outputs"]["stage_13_write_summary"])