# Workflow Overview  
## reproducible_pipeline_framework v2

---

## 1. Purpose

This document describes the end-to-end workflow implemented in Version 2 of
`reproducible_pipeline_framework`.

It provides a conceptual and operational overview of:

- pipeline stages
- execution flow
- execution modes
- artifact progression
- automation vs. manual review boundaries

This document complements:

- `SOP_pipeline_example.md`
- `state_contract_v2.md`
- `architecture.md`

---

## 2. High-Level Pipeline Flow

The pipeline follows a staged, linear workflow where each stage:

- consumes structured inputs
- produces defined artifacts
- updates shared pipeline state
- emits QC and traceability information

### Conceptual Flow

```text
DATA
  → ALIGNMENT
    → BAM PROCESSING
      → QC
        → VARIANT CALLING
          → VCF NORMALIZATION
            → ANNOTATION
              → FILTERING + PARTITIONING
                → INTERPRETATION
                  → PRIORITIZATION
                    → VALIDATION PREP
                      → SUMMARY REPORTING
```

---

## 3. Execution Modes

The pipeline supports two execution modes:

### Full Pipeline Mode

Used when starting from sequencing data.

Input:
- paired FASTQ files

Stages executed:
- Stage 01 → Stage 13

This mode performs:
- alignment
- BAM processing
- variant calling
- downstream interpretation

---

### Annotation-Only Mode

Used when a VCF is already available.

Input:
- VCF file

Stages executed:
- Stage 01 (mode detection)
- Stage 06 → Stage 13

This mode skips:
- alignment
- BAM processing
- variant calling

---

## 4. Stage Overview

### Stage 01 — Load Data

- validates mode-specific inputs
- initializes sample metadata
- records input files in state

---

### Stage 02 — Align Data

- aligns sequencing reads
- generates aligned BAM

---

### Stage 03 — Process BAM

- sorts BAM
- indexes BAM

---

### Stage 04 — QC Aligned Reads

- generates alignment QC metrics
- writes QC report

---

### Stage 05 — Call Variants

- generates raw VCF from BAM

---

### Stage 06 — Normalize VCF

- standardizes variant representation
- cleans malformed records

---

### Stage 07 — Annotate Variants

- adds population, clinical, and functional annotations
- outputs annotated VCF and table

---

### Stage 08 — Filter and Partition

- applies global filtering thresholds
- partitions into:
  - coding track
  - non-coding track

---

### Stage 09 — Interpret Coding Variants

- interprets coding-track variants
- integrates functional and clinical evidence

---

### Stage 10 — Interpret Non-Coding Variants

- interprets non-coding variants
- emphasizes splice and regulatory signals

---

### Stage 11 — Prioritize Variants

- merges coding and non-coding interpretations
- assigns final cross-track prioritization

---

### Stage 12 — Validation Preparation

- performs automated validation pre-checks
- generates manual-review candidate list
- prepares IGV handoff artifacts

**Important:**  
IGV review is not automated by the pipeline.

---

### Stage 13 — Summary Reporting

- aggregates metrics
- writes human-readable summary
- writes machine-readable summary table
- finalizes run outputs

---

## 5. Data and Artifact Flow

Artifacts are produced in a predictable directory structure:

```text
data/
  interim/
  processed/

results/
  runs/
    <run_id>/
      final/
      validation/
      reports/
      logs/
```

Each stage writes outputs to disk and records their paths in `state`.

---

## 6. Automation vs Manual Boundaries

### Fully Automated

- alignment
- BAM processing
- QC
- variant calling
- annotation
- filtering
- interpretation
- prioritization
- validation preparation
- summary reporting

### Manual / Human-in-the-loop

- IGV review of prioritized loci
- biological interpretation decisions

---

## 7. State and Traceability

All stages share a common `state` object that tracks:

- inputs
- outputs
- QC metrics
- warnings
- errors
- run metadata

This enables:

- reproducibility
- auditing
- debugging
- downstream extension

---

## 8. Intended Use

This workflow is designed to:

- demonstrate a reproducible pipeline framework
- serve as a scaffold for future pipelines
- support experimentation and extension
- enable portfolio-grade demonstration of pipeline engineering

It is not intended for clinical deployment.

---

# End of Workflow Overview