# State Contract v2  
## reproducible_pipeline_framework

---

## Purpose

This document defines the Version 2 `state` object contract for `reproducible_pipeline_framework`.

The `state` object is the central execution record passed between stages during a pipeline run.

Its purpose is to provide:

- explicit stage-to-stage data flow
- clear ownership of inputs and outputs
- reproducibility and traceability
- a compact execution record
- support for multiple execution modes

Version 2 replaces the looser Version 1 state pattern with a more explicit nested dictionary contract.

This document serves as the source of truth for:

- stage read/write expectations
- state layout
- error-handling behavior
- execution-mode support

---

## Design Principles

The v2 `state` object should follow these principles:

1. The `state` object remains a plain Python dictionary.
2. The `state` object is nested and organized by responsibility.
3. The `state` object should prefer file paths over large in-memory payloads.
4. Each stage should read only the keys it requires.
5. Each stage should write only the keys it produces.
6. Missing required keys should cause explicit failure with clear logging.
7. Large artifacts such as FASTQ, BAM, and VCF files should be stored on disk and referenced in `state` by path.
8. The `state` object should support both:
   - `full_pipeline`
   - `annotation_only`

---

## Top-Level State Structure

The canonical v2 `state` object should use this structure:

    state = {
        "run": {},
        "sample": {},
        "inputs": {},
        "artifacts": {},
        "qc": {},
        "annotations": {},
        "tracks": {},
        "reports": {},
        "stage_outputs": {},
        "warnings": [],
        "errors": [],
    }

Each top-level section has a specific purpose and should not be used interchangeably.

---

## Top-Level Sections

## 1. `run`

Purpose:
- store run-wide execution metadata

Typical contents:
- `run_id`
- `mode`
- `status`
- `start_time`
- `end_time`
- `pipeline_version`
- `config_path`
- `log_file`
- `metadata_file`

Example:

    state["run"] = {
        "run_id": "run_2026_04_13_101500",
        "mode": "full_pipeline",
        "status": "running",
        "start_time": "2026-04-13T10:15:00",
        "end_time": None,
        "pipeline_version": "2.0.0",
        "config_path": "config/config.yaml",
        "log_file": "results/runs/run_2026_04_13_101500/logs/pipeline.log",
        "metadata_file": "results/runs/run_2026_04_13_101500/metadata.json",
    }

---

## 2. `sample`

Purpose:
- store sample-specific metadata

Typical contents:
- `sample_id`
- `cohort_id` (optional)
- `assay_type`
- `reference_genome`

Example:

    state["sample"] = {
        "sample_id": "toy_sample_01",
        "cohort_id": None,
        "assay_type": "WGS",
        "reference_genome": "GRCh38",
    }

---

## 3. `inputs`

Purpose:
- record raw input paths and user-supplied entry artifacts

Typical contents:
- `fastq_1`
- `fastq_2`
- `input_vcf`
- `mode_confirmed`

Rules:
- `full_pipeline` mode should use FASTQ input fields
- `annotation_only` mode should use `input_vcf`

Example:

    state["inputs"] = {
        "fastq_1": "data/example/example_R1.fastq",
        "fastq_2": "data/example/example_R2.fastq",
        "input_vcf": None,
        "mode_confirmed": "full_pipeline",
    }

---

## 4. `artifacts`

Purpose:
- record paths to pipeline-generated artifacts

Typical contents:
- `aligned_bam`
- `sorted_bam`
- `bam_index`
- `raw_vcf`
- `normalized_vcf`
- `annotated_vcf`
- `annotated_table`
- `coding_track_table`
- `noncoding_track_table`
- `interpreted_coding_table`
- `interpreted_noncoding_table`
- `prioritized_table`
- `validation_notes`
- `summary_report`

Rules:
- artifacts should be stored as paths
- file paths should point to on-disk outputs
- avoid storing large binary objects in memory

Example:

    state["artifacts"] = {
        "aligned_bam": "data/interim/aligned.bam",
        "sorted_bam": "data/interim/aligned.sorted.bam",
        "bam_index": "data/interim/aligned.sorted.bam.bai",
        "raw_vcf": "data/interim/raw_variants.vcf",
        "normalized_vcf": "data/interim/normalized_variants.vcf",
        "annotated_vcf": "data/processed/annotated_variants.vcf",
        "annotated_table": "data/processed/annotated_variants.tsv",
        "coding_track_table": "results/runs/<run_id>/final/coding_track.tsv",
        "noncoding_track_table": "results/runs/<run_id>/final/noncoding_track.tsv",
        "interpreted_coding_table": "results/runs/<run_id>/final/interpreted_coding.tsv",
        "interpreted_noncoding_table": "results/runs/<run_id>/final/interpreted_noncoding.tsv",
        "prioritized_table": "results/runs/<run_id>/final/prioritized_variants.tsv",
        "validation_notes": None,
        "summary_report": "results/runs/<run_id>/reports/pipeline_summary.txt",
    }

---

## 5. `qc`

Purpose:
- store stage-specific QC summaries and validation metrics

Typical contents:
- `input_qc`
- `alignment_qc`
- `bam_processing_qc`
- `variant_calling_qc`
- `annotation_qc`
- `filtering_qc`
- `validation_qc`

Rules:
- QC summaries should be compact and serializable
- QC should store metrics, counts, flags, and summary dictionaries

Example:

    state["qc"] = {
        "input_qc": {
            "files_found": True,
            "read_count_estimate": 1000,
        },
        "alignment_qc": {
            "alignment_completed": True,
            "mapping_rate": 0.98,
        },
        "bam_processing_qc": {
            "sorted_bam_created": True,
            "bam_index_created": True,
        },
        "variant_calling_qc": {
            "variant_count": 52,
            "vcf_created": True,
        },
    }

---

## 6. `annotations`

Purpose:
- record annotation-layer metadata and resources used

Typical contents:
- `resources_used`
- `annotation_fields_present`
- `annotation_completeness`
- `ai_annotations_used`

Example:

    state["annotations"] = {
        "resources_used": ["ANNOVAR", "ClinVar", "gnomAD", "AlphaMissense", "SpliceAI"],
        "annotation_fields_present": [
            "gene_symbol",
            "variant_type",
            "clinvar_classification",
            "af_gnomad",
            "alphamissense_score",
            "spliceai_score",
        ],
        "annotation_completeness": {
            "gene_symbol": 1.0,
            "clinvar_classification": 0.85,
            "af_gnomad": 0.95,
        },
        "ai_annotations_used": ["AlphaMissense", "SpliceAI"],
    }

---

## 7. `tracks`

Purpose:
- store track-specific summaries and table references for coding and non-coding branches

Typical contents:
- `coding`
- `noncoding`

Example:

    state["tracks"] = {
        "coding": {
            "table_path": "results/runs/<run_id>/final/coding_track.tsv",
            "variant_count": 18,
            "prioritization_summary": {
                "pathogenic": 2,
                "vus": 5,
            },
        },
        "noncoding": {
            "table_path": "results/runs/<run_id>/final/noncoding_track.tsv",
            "variant_count": 7,
            "alphagenome_used": False,
            "prioritization_summary": {
                "splice_relevant": 3,
                "regulatory_candidates": 2,
            },
        },
    }

---

## 8. `reports`

Purpose:
- store paths and metadata related to final reporting

Typical contents:
- `summary_report`
- `summary_table`
- `report_line_count`

Example:

    state["reports"] = {
        "summary_report": "results/runs/<run_id>/reports/pipeline_summary.txt",
        "summary_table": "results/runs/<run_id>/reports/prioritized_variant_summary.tsv",
        "report_line_count": 42,
    }

---

## 9. `stage_outputs`

Purpose:
- preserve per-stage structured summaries

Rules:
- each stage should write a compact summary of what it did
- these summaries should be easy to inspect and serialize
- this is the main place to store stage-local counts and output summaries

Example:

    state["stage_outputs"] = {
        "stage_01_load_data": {
            "mode": "full_pipeline",
            "input_files_found": True,
        },
        "stage_05_call_variants": {
            "raw_variant_count": 52,
            "raw_vcf": "data/interim/raw_variants.vcf",
        },
        "stage_11_prioritize_variants": {
            "final_row_count": 9,
            "prioritized_gene_count": 4,
        },
    }

---

## 10. `warnings`

Purpose:
- accumulate non-fatal warnings

Rules:
- warnings should be strings or compact structured dicts
- warnings should remain serializable

Example:

    state["warnings"] = [
        "Stage 07: ExAC resource not available, continuing without legacy AF annotation.",
        "Stage 10: AlphaGenome disabled for this run.",
    ]

---

## 11. `errors`

Purpose:
- accumulate fatal or stage-level error summaries

Rules:
- errors should be explicit and inspectable
- errors should not replace proper exception raising and logging
- they should complement logs and metadata

Example:

    state["errors"] = [
        {
            "stage": "stage_05_call_variants",
            "message": "VCF file was not created.",
        }
    ]

---

## Required vs Optional Keys

### Required Top-Level Keys

The following top-level keys must always exist:

- `run`
- `sample`
- `inputs`
- `artifacts`
- `qc`
- `annotations`
- `tracks`
- `reports`
- `stage_outputs`
- `warnings`
- `errors`

### Optional Nested Keys

Nested keys may be absent or set to `None` depending on:

- execution mode
- stage completion
- resource availability
- optional tool usage

Example:
- `state["inputs"]["input_vcf"]` may be `None` in `full_pipeline`
- `state["inputs"]["fastq_1"]` may be `None` in `annotation_only`

---

## Execution Mode Behavior

## Mode 1 — `full_pipeline`

Expected entry:
- FASTQ

Typical required input fields:
- `state["inputs"]["fastq_1"]`
- `state["inputs"]["fastq_2"]`

Typical generated artifacts:
- BAM
- BAI
- raw VCF
- normalized VCF
- annotation outputs
- track-specific tables
- prioritized report

## Mode 2 — `annotation_only`

Expected entry:
- VCF

Typical required input field:
- `state["inputs"]["input_vcf"]`

Typical skipped or mocked upstream artifacts:
- alignment BAM
- sorted BAM
- BAM index
- raw variant calling output

This mode should begin conceptually at:
- normalization
- annotation
- filtering
- interpretation
- reporting

---

## Stage Read/Write Expectations

The following summaries describe what each stage is expected to read from and write to `state`.

## Stage 01 — Load Data

Reads:
- config values
- input FASTQ path(s) or input VCF path

Writes:
- `state["run"]["mode"]`
- `state["sample"]`
- `state["inputs"]`
- `state["qc"]["input_qc"]`
- `state["stage_outputs"]["stage_01_load_data"]`

---

## Stage 02 — Align Data

Reads:
- `state["inputs"]["fastq_1"]`
- `state["inputs"]["fastq_2"]`

Writes:
- `state["artifacts"]["aligned_bam"]`
- `state["qc"]["alignment_qc"]`
- `state["stage_outputs"]["stage_02_align_data"]`

---

## Stage 03 — Process BAM

Reads:
- `state["artifacts"]["aligned_bam"]`

Writes:
- `state["artifacts"]["sorted_bam"]`
- `state["artifacts"]["bam_index"]`
- `state["qc"]["bam_processing_qc"]`
- `state["stage_outputs"]["stage_03_process_bam"]`

---

## Stage 04 — QC Aligned Reads

Reads:
- `state["artifacts"]["sorted_bam"]`
- `state["artifacts"]["bam_index"]`

Writes:
- `state["qc"]["alignment_qc"]`
- `state["stage_outputs"]["stage_04_qc_aligned_reads"]`

---

## Stage 05 — Call Variants

Reads:
- `state["artifacts"]["sorted_bam"]`
- `state["artifacts"]["bam_index"]`

Writes:
- `state["artifacts"]["raw_vcf"]`
- `state["qc"]["variant_calling_qc"]`
- `state["stage_outputs"]["stage_05_call_variants"]`

---

## Stage 06 — Normalize VCF

Reads:
- `state["artifacts"]["raw_vcf"]` or `state["inputs"]["input_vcf"]`

Writes:
- `state["artifacts"]["normalized_vcf"]`
- `state["qc"]["variant_calling_qc"]`
- `state["stage_outputs"]["stage_06_normalize_vcf"]`

---

## Stage 07 — Annotate Variants

Reads:
- `state["artifacts"]["normalized_vcf"]`

Writes:
- `state["artifacts"]["annotated_vcf"]`
- `state["artifacts"]["annotated_table"]`
- `state["annotations"]`
- `state["stage_outputs"]["stage_07_annotate_variants"]`

---

## Stage 08 — Filter and Partition

Reads:
- `state["artifacts"]["annotated_table"]`

Writes:
- `state["artifacts"]["coding_track_table"]`
- `state["artifacts"]["noncoding_track_table"]`
- `state["tracks"]["coding"]`
- `state["tracks"]["noncoding"]`
- `state["stage_outputs"]["stage_08_filter_and_partition"]`

---

## Stage 09 — Interpret Coding

Reads:
- `state["artifacts"]["coding_track_table"]`

Writes:
- `state["artifacts"]["interpreted_coding_table"]`
- `state["tracks"]["coding"]`
- `state["stage_outputs"]["stage_09_interpret_coding"]`

---

## Stage 10 — Interpret Noncoding

Reads:
- `state["artifacts"]["noncoding_track_table"]`

Writes:
- `state["artifacts"]["interpreted_noncoding_table"]`
- `state["tracks"]["noncoding"]`
- `state["stage_outputs"]["stage_10_interpret_noncoding"]`

---

## Stage 11 — Prioritize Variants

Reads:
- `state["artifacts"]["interpreted_coding_table"]`
- `state["artifacts"]["interpreted_noncoding_table"]`

Writes:
- `state["artifacts"]["prioritized_table"]`
- `state["stage_outputs"]["stage_11_prioritize_variants"]`

---

## Stage 12 — Validate Variants

Reads:
- `state["artifacts"]["prioritized_table"]`
- optional BAM-related artifacts if available

Writes:
- `state["artifacts"]["validation_notes"]`
- `state["qc"]["validation_qc"]`
- `state["stage_outputs"]["stage_12_validate_variants"]`

---

## Stage 13 — Write Summary

Reads:
- `state["artifacts"]["prioritized_table"]`
- `state["qc"]`
- `state["annotations"]`
- `state["tracks"]`
- `state["stage_outputs"]`

Writes:
- `state["reports"]`
- `state["run"]["status"]`
- `state["run"]["end_time"]`
- `state["stage_outputs"]["stage_13_write_summary"]`

---

## Error Handling Rules

If a stage cannot find a required input in `state`, it must:

1. log the failure clearly
2. append a clear summary to `state["errors"]`
3. fail explicitly rather than silently continuing

Warnings should be recorded in `state["warnings"]`.

---

## Serialization Rule

The `state` object should remain serializable.

This means:
- prefer strings, numbers, booleans, lists, and dicts
- prefer file paths over in-memory heavy objects
- avoid storing large binary payloads directly in `state`

If temporary in-memory objects are needed during a stage, they should not become the long-term canonical execution record.

---

## Relationship to Implementation

The `state` contract defined here should guide:

- stage implementation
- pipeline runner behavior
- metadata generation
- logging
- downstream documentation

Any future code refactor should remain consistent with this contract unless the contract itself is deliberately revised and versioned.

---

## Immediate Use

This document should be used in v2 development to:

- scaffold the 13-stage pipeline
- update `pipeline_runner.py`
- update `config/config.yaml`
- enforce consistent stage boundaries
- support both execution modes
- prepare clean transfer of this architecture into `variant_annotation_pipeline`

---

# End of State Contract