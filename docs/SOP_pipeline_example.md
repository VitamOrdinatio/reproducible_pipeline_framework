# SOP Pipeline Example  
## Variant Discovery and Dual-Track Interpretation Pipeline  
### reproducible_pipeline_framework v2

---

## 1. Purpose

This document defines the canonical example pipeline implemented in Version 2 of `reproducible_pipeline_framework`.

The purpose of this example is to demonstrate how a reproducible, configuration-driven bioinformatics pipeline can process sequencing data from initial input through:

- alignment
- BAM processing
- quality control
- variant calling
- variant normalization
- annotation
- dual-track interpretation
- prioritization
- validation preparation
- summary reporting

This pipeline is designed as a **framework demonstration**, not a clinically validated diagnostic workflow.

It is also intended to serve as the architectural precursor to the future `variant_annotation_pipeline` repository.

---

## 2. Scope

This SOP describes a 13-stage traditional genomics workflow that supports two execution modes:

- `full_pipeline`
  - FASTQ → BAM → VCF → annotation → prioritization
- `annotation_only`
  - VCF → normalization → annotation → prioritization

The current framework implementation is optimized for:

- toy/example data
- local execution
- explicit state tracking
- staged artifact creation
- reproducible output generation

The current version uses lightweight or placeholder implementations for several tool-oriented steps so that the framework remains runnable and easy to inspect.

---

## 3. Inputs

## 3.1 Full Pipeline Mode

Input files:
- paired FASTQ files

Examples:
- `data/example/example_R1.fastq`
- `data/example/example_R2.fastq`

These represent sequencing reads that enter the full pipeline workflow.

---

## 3.2 Annotation-Only Mode

Input files:
- VCF file

Example:
- `data/example/example_variants.vcf`

This mode bypasses alignment and variant calling and begins at VCF normalization.

---

## 3.3 Metadata

Run metadata includes:
- sample identifier
- execution mode
- reference genome
- pipeline version
- config path
- run identifier

Repository mapping:
- config → `config/config.yaml`
- metadata → `results/runs/<run_id>/metadata.json`

---

## 4. Outputs

## 4.1 Interim Outputs

Examples:
- aligned BAM
- sorted BAM
- BAM index
- raw VCF
- normalized VCF

Repository mapping:
- `data/interim/`

---

## 4.2 Processed Outputs

Examples:
- annotated VCF
- annotated variant table

Repository mapping:
- `data/processed/`

---

## 4.3 Final Outputs

Examples:
- filtered variants
- coding-track table
- non-coding-track table
- interpreted coding variants
- interpreted non-coding variants
- prioritized variant table

Repository mapping:
- `results/runs/<run_id>/final/`

---

## 4.4 Validation Outputs

Examples:
- validation notes
- IGV review candidate table

Repository mapping:
- `results/runs/<run_id>/validation/`

---

## 4.5 Summary Outputs

Examples:
- pipeline summary report
- prioritized variant summary table

Repository mapping:
- `results/runs/<run_id>/reports/`

---

## 5. Software and Environment

This framework currently models the following tool classes:

- BWA-MEM or equivalent for alignment
- samtools for BAM processing and QC
- GATK or equivalent for variant calling and normalization
- ANNOVAR or equivalent for annotation
- IGV for optional manual review

The current framework implementation uses lightweight or placeholder logic for several of these steps so that the repository remains runnable without heavy external setup.

Environment assumptions:
- Linux workstation
- Python-based execution
- dependencies defined in `requirements.txt`
- run entry point via `run_pipeline.py`

---

## 6. Pipeline Overview

High-level workflow:

`FASTQ → ALIGNMENT → BAM PROCESSING → QC → VARIANT CALLING → VCF NORMALIZATION → ANNOTATION → FILTERING / PARTITIONING → INTERPRETATION → PRIORITIZATION → VALIDATION PREP → SUMMARY`

In annotation-only mode:

`VCF → NORMALIZATION → ANNOTATION → FILTERING / PARTITIONING → INTERPRETATION → PRIORITIZATION → VALIDATION PREP → SUMMARY`

Repository mapping:
- entry point → `run_pipeline.py`
- orchestration → `src/pipeline_runner.py`
- stage modules → `pipeline/`

---

## 7. Detailed Procedure

---

### Step 1 — Load Data

**Module:** `pipeline/stage_01_load_data.py`

**Input:**
- FASTQ pair in `full_pipeline`
- VCF in `annotation_only`

**Description:**
- Validate mode-specific inputs
- Record input metadata
- Initialize state-aware input QC

**Rationale:**
- Ensure correct entry conditions before execution

**QC:**
- required files exist
- file count recorded
- mode confirmed

---

### Step 2 — Align Data

**Module:** `pipeline/stage_02_align_data.py`

**Input:**
- FASTQ pair

**Tool class:**
- BWA-MEM or equivalent

**Description:**
- Align reads to the reference genome
- Create aligned BAM artifact

**Rationale:**
- Map sequencing reads to genomic coordinates

**Output:**
- aligned BAM

**QC:**
- FASTQ read counts recorded
- BAM artifact created
- alignment state updated

---

### Step 3 — Process BAM

**Module:** `pipeline/stage_03_process_bam.py`

**Input:**
- aligned BAM

**Tool class:**
- samtools

**Description:**
- Sort BAM
- Index BAM

**Rationale:**
- Prepare BAM for QC and downstream calling

**Output:**
- sorted BAM
- BAM index

**QC:**
- sorted BAM exists
- BAM index exists
- processing summary recorded

---

### Step 4 — QC Aligned Reads

**Module:** `pipeline/stage_04_qc_aligned_reads.py`

**Input:**
- sorted BAM
- BAM index

**Tool class:**
- samtools stats / flagstat or equivalent

**Description:**
- Generate alignment QC summary
- Write QC report artifact

**Rationale:**
- Assess alignment readiness for calling

**Output:**
- aligned-read QC report

**QC metrics:**
- total reads
- mapped reads
- mapping rate
- BAM artifact presence

---

### Step 5 — Call Variants

**Module:** `pipeline/stage_05_call_variants.py`

**Input:**
- sorted BAM
- BAM index

**Tool class:**
- GATK HaplotypeCaller or equivalent

**Description:**
- Call sequence variants from processed BAM

**Rationale:**
- Identify deviations from the reference genome

**Output:**
- raw VCF

**QC:**
- VCF file generated successfully
- variant count recorded
- no malformed records detected

---

### Step 6 — VCF Normalization and Cleaning

**Module:** `pipeline/stage_06_normalize_vcf.py`

**Input:**
- raw VCF in `full_pipeline`
- input VCF in `annotation_only`

**Tool class:**
- GATK or equivalent

**Description:**
- Normalize chromosome naming
- remove malformed entries
- standardize variant representation

**Rationale:**
- Ensure consistent representation for annotation

**Output:**
- normalized VCF

**QC:**
- normalized VCF created
- malformed records removed or flagged
- normalized variant count recorded

---

### Step 7 — Annotation (No Filtering)

**Module:** `pipeline/stage_07_annotate_variants.py`

**Input:**
- normalized VCF

**Tool classes / resources:**
- ANNOVAR or equivalent
- gnomAD
- ExAC
- 1000 Genomes
- ClinVar
- AlphaMissense
- SpliceAI

**Description:**
- Add biological, population-frequency, clinical, and AI-style annotation fields

**Rationale:**
- Enrich variants with interpretation-relevant context

**Output:**
- annotated VCF
- annotated variant table

**Output Location:**
- `data/processed/`

**QC:**
- annotation completed successfully
- required annotation fields present
- annotation completeness metrics recorded

#### Annotation Types

##### Structural / Functional
- gene symbol
- consequence
- variant class

##### Population Frequency
- `AF_gnomAD`
- `AF_ExAC`
- `AF_1KGenomes`

##### Clinical Annotation
- `ClinVar_classification`

##### AI-Based Annotation
- `AlphaMissense_score` for missense variants
- `SpliceAI_score` for splice-relevant variants

##### Variant Classification Field
- `variant_type = {coding, non-coding}`

### Important Principle

No variants are removed at this stage.

Annotation adds information; it does not filter variants.

---

### Step 8 — Global Filtering and Partitioning into Dual Tracks

**Module:** `pipeline/stage_08_filter_and_partition.py`

**Input:**
- annotated variant table

**Description:**
- Remove variants with high allele frequency
- Apply AF thresholds from `config/config.yaml`
- Partition retained variants into:
  - coding track
  - non-coding track

**Rationale:**
- Separate broad annotation from track-specific interpretation logic

**Output:**
- filtered variant table
- coding-track table
- non-coding-track table

**QC:**
- filtered count recorded
- coding count recorded
- non-coding count recorded

#### Track A — Coding Variants
Examples:
- missense
- nonsense
- frameshift
- splice_site

#### Track B — Non-Coding Variants
Examples:
- intronic
- intergenic
- regulatory

---

### Step 9 — Interpretation (Track A: Coding)

**Module:** `pipeline/stage_09_interpret_coding.py`

**Input:**
- coding-track table

**Evidence integration:**
- ClinVar
- AlphaMissense
- SpliceAI where relevant

**Interpretation logic:**
- rare + damaging → prioritize
- known or likely pathogenic → prioritize
- VUS with AI support → intermediate priority

**Output:**
- interpreted coding table

**QC:**
- coding variant count recorded
- coding gene count recorded
- interpretation class counts recorded

---

### Step 10 — Interpretation (Track B: Non-Coding)

**Module:** `pipeline/stage_10_interpret_noncoding.py`

**Input:**
- non-coding-track table

**Evidence integration:**
- SpliceAI
- limited ClinVar signal
- optional AlphaGenome-style logic

**Interpretation logic:**
- splice-relevant non-coding candidates → prioritize
- regulatory candidates → prioritize conditionally
- lower-confidence non-coding variants → lower priority

**Output:**
- interpreted non-coding table

**QC:**
- non-coding variant count recorded
- non-coding gene count recorded
- interpretation class counts recorded

### Important Principle

AlphaGenome-style support is optional and selective.  
It is not required for the current framework demonstration.

---

### Step 11 — Variant Prioritization

**Module:** `pipeline/stage_11_prioritize_variants.py`

**Input:**
- interpreted coding table
- interpreted non-coding table

**Description:**
- Combine both tracks
- assign final cross-track ranking
- write unified prioritized variant table

**Priority score considers:**
- rarity
- functional consequence
- clinical evidence
- coding interpretation rank
- non-coding interpretation rank
- splice-related support

**Output:**
- prioritized variant table

**QC:**
- prioritized variant count recorded
- prioritized gene count recorded
- track counts recorded

---

### Step 12 — Validation Preparation for Manual IGV Review

**Module:** `pipeline/stage_12_validate_variants.py`

**Input:**
- prioritized variant table
- upstream BAM/VCF-derived context from earlier stages

**Tool class:**
- IGV is used as a downstream manual review tool

**Description:**
- Perform automated validation pre-checks
- generate validation notes
- generate a candidate table for optional manual IGV review

**Rationale:**
- Separate automated pipeline validation from analyst-driven visual review

**Output:**
- validation notes
- IGV review candidate list

**QC:**
- candidate count recorded
- warnings recorded
- validation outputs created successfully

### Important Clarification

IGV review is **not automated by the pipeline**.

Instead, the pipeline prepares a structured handoff for optional human inspection of:
- read depth
- allele balance
- strand bias
- local alignment artifacts

---

### Step 13 — Generate Summary Reports

**Module:** `pipeline/stage_13_write_summary.py`

**Input:**
- prioritized variant table
- QC summaries
- annotation summary
- validation summary
- artifact registry
- stage output summaries

**Description:**
- Generate human-readable summary report
- generate compact machine-readable summary table

**Rationale:**
- Provide a reproducible run summary for inspection, debugging, and reuse

**Output:**
- pipeline summary report
- prioritized variant summary table

**Output Location:**
- `results/runs/<run_id>/reports/`

**QC:**
- summary files exist
- artifact completeness recorded
- warnings and errors included in report

---

## 8. Biological Interpretation

Variants are interpreted in the context of:

- gene function
- predicted functional consequence
- coding vs non-coding classification
- population frequency
- clinical annotation
- AI-derived support scores where available

Coding variants are generally prioritized using:
- ClinVar
- functional consequence
- AlphaMissense
- SpliceAI where applicable

Non-coding variants are generally prioritized using:
- splice relevance
- regulatory classification
- optional AI-style support
- rarity

This framework uses simplified interpretation logic for demonstration purposes.

---

## 9. Assumptions

- reference genome is accurate
- sequencing quality is sufficient
- annotation sources are representative
- toy dataset size is appropriate for local execution
- manual IGV review, when used, is performed by the user outside the automated pipeline

---

## 10. Limitations

- placeholder logic is used for several tool-oriented stages
- no structural variant support
- non-coding interpretation remains simplified
- AI support is illustrative, not definitive
- not clinically validated
- IGV review is not automated

This pipeline is intended for framework demonstration and development, not clinical deployment.

---

## 11. Reproducibility

Reproducibility is ensured by:

- configuration-driven execution
- explicit stage modules
- state-based orchestration
- config snapshot saved per run
- metadata tracking
- structured run directories
- deterministic artifact generation for example data

### Repository Mapping
- config snapshot → `results/runs/<run_id>/config_used.yaml`
- metadata → `results/runs/<run_id>/metadata.json`
- logs → `results/runs/<run_id>/logs/pipeline.log`

Each run directory is intended to function as a self-contained record of execution.

---

## 12. Logging and Traceability

Each run produces:

- pipeline log file
- execution trace
- metadata record
- stage-specific outputs
- validation preparation artifacts
- final summary artifacts

All major pipeline events are recorded in the pipeline log.

Stage boundaries are explicit and traceable through:
- `state`
- artifact paths
- stage summaries
- run directories

---

## 13. Future Extensions

Potential improvements include:

- integrate real external tools directly
- add richer cohort-level support
- incorporate OMIM and HGMD where appropriate
- add structural variant support
- improve regulatory annotation
- expand manual-review integration support
- add integration tests and formal validation harnesses

---

## 14. Final Conceptual Model

Workflow:

`DATA → PROCESSING → ANNOTATION → PARTITION → INTERPRETATION → PRIORITIZATION → VALIDATION PREP → REPORTING`

Handling coding variants:

`Coding variants = ClinVar + consequence + AlphaMissense + SpliceAI`

Handling non-coding variants:

`Non-coding variants = rarity + SpliceAI + regulatory logic + optional AlphaGenome-style support`

---

## 15. State Object Contract

Each pipeline stage receives a shared `state` object and returns an updated `state` object.

The purpose of the `state` object is to provide a single, explicit, traceable record of pipeline execution without relying on global variables or implicit dependencies.

The `state` object stores:
- run metadata
- configuration values
- sample metadata
- file paths produced by prior stages
- QC summaries
- annotation metadata
- track-specific outputs
- prioritization outputs
- validation outputs
- report paths
- warnings and errors

### Design Principles

1. The `state` object is serializable.
2. The `state` object prefers file paths over large in-memory payloads.
3. Each stage reads only the keys it requires and writes only the keys it produces.
4. Missing required keys should cause clear failure with explicit error logging.
5. Large artifacts such as FASTQ, BAM, and VCF are persisted to disk and referenced in `state` by path.
6. The `state` object supports both:
   - `full_pipeline`
   - `annotation_only`

---

## 16. Stage Read/Write Contract

Each stage must declare, explicitly or through implementation structure:

- required inputs from `state`
- outputs written back to `state`
- files created on disk
- QC summaries produced
- warnings or errors generated

This contract ensures:
- stage boundaries remain explicit
- pipeline execution remains traceable
- downstream repos can inherit the same execution philosophy

---

# End of SOP Pipeline Example