# QC Template  
## reproducible_pipeline_framework v2

---

## 1. Purpose

This document defines the expected quality control (QC) checks, metrics, and failure conditions for each stage of the v2 pipeline.

QC in this framework is:

- automated where possible
- recorded in `state["qc"]`
- surfaced in run metadata and summary reports
- designed to support reproducibility and troubleshooting

This document complements:

- `state_contract_v2.md`
- `workflow.md`
- `architecture.md`

---

## 2. QC Philosophy

The pipeline follows these QC principles:

- fail fast when critical inputs are missing
- record metrics even when stages succeed
- distinguish warnings from fatal errors
- preserve partial outputs for debugging

QC is not intended to be exhaustive or clinical-grade in this framework; it provides structural and sanity checks appropriate for a scaffold pipeline.

---

## 3. Stage-Level QC Requirements

---

### Stage 01 — Load Data

**Checks:**

- required input files exist
- execution mode is valid
- file paths are readable

**Metrics:**

- FASTQ files present (if full_pipeline)
- VCF present (if annotation_only)

**Failure Conditions:**

- missing required inputs
- invalid execution mode

---

### Stage 02 — Align Data

**Checks:**

- FASTQ files exist and are readable
- alignment output produced

**Metrics:**

- read count
- alignment artifact exists

**Failure Conditions:**

- missing FASTQ files
- alignment output not generated

---

### Stage 03 — Process BAM

**Checks:**

- aligned BAM exists
- sorted BAM produced
- BAM index produced

**Metrics:**

- BAM file sizes
- presence of index file

**Failure Conditions:**

- missing aligned BAM
- failed sort or index

---

### Stage 04 — QC Aligned Reads

**Checks:**

- sorted BAM exists
- index file exists

**Metrics:**

- mapped read count
- total read count
- mapping rate (approximate)

**Failure Conditions:**

- missing BAM or index

---

### Stage 05 — Call Variants

**Checks:**

- sorted BAM exists
- BAM index exists
- VCF produced

**Metrics:**

- variant count
- malformed records detected

**Failure Conditions:**

- missing BAM or index
- no VCF generated

---

### Stage 06 — Normalize VCF

**Checks:**

- input VCF exists
- normalized VCF written

**Metrics:**

- normalized variant count
- malformed records removed

**Failure Conditions:**

- missing input VCF
- malformed VCF format

---

### Stage 07 — Annotate Variants

**Checks:**

- normalized VCF exists
- annotation table produced

**Metrics:**

- annotation completion
- presence of key annotation fields

**Failure Conditions:**

- missing normalized VCF
- annotation output not generated

---

### Stage 08 — Filter and Partition

**Checks:**

- annotated table exists
- filtering thresholds applied

**Metrics:**

- variants before filtering
- variants after filtering
- coding count
- non-coding count

**Failure Conditions:**

- missing annotation table

---

### Stage 09 — Interpret Coding Variants

**Checks:**

- coding-track table exists

**Metrics:**

- coding variants interpreted
- interpretation class distribution

**Failure Conditions:**

- missing coding-track table

---

### Stage 10 — Interpret Non-Coding Variants

**Checks:**

- non-coding-track table exists

**Metrics:**

- non-coding variants interpreted
- interpretation class distribution

**Failure Conditions:**

- missing non-coding-track table

---

### Stage 11 — Prioritize Variants

**Checks:**

- interpreted coding and non-coding tables exist

**Metrics:**

- prioritized variant count
- track distribution

**Failure Conditions:**

- missing interpreted tables

---

### Stage 12 — Validation Preparation

**Checks:**

- prioritized variant table exists

**Metrics:**

- candidate count for IGV review
- validation warnings

**Failure Conditions:**

- missing prioritized table

---

### Stage 13 — Summary Reporting

**Checks:**

- all required upstream artifacts exist

**Metrics:**

- report completeness
- summary table written
- QC summary present

**Failure Conditions:**

- missing critical upstream artifacts

---

## 4. Error Handling

Errors are recorded in:

```python
state["errors"]
```

Warnings are recorded in:

```python
state["warnings"]
```

Fatal errors halt pipeline execution.

---

## 5. QC Outputs

QC artifacts may include:

- alignment QC reports
- variant statistics
- validation notes
- run metadata

QC information is surfaced in:

- run logs
- metadata.json
- summary report

---

## 6. Extensibility

Future versions may:

- integrate richer QC metrics
- support formal validation frameworks
- add cohort-level QC
- integrate external QC tools

---

# End of QC Template