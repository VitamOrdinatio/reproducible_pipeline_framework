# SOP Pipeline Example  
## Variant Interpretation / Annotation Pipeline

---

## 0. Relationship to Pipeline Implementation

This SOP describes a concrete pipeline implemented within the repository framework.

Each procedural step maps directly to:

- Pipeline modules → `pipeline/stage_*.py`  
- Configuration → `config/config.yaml`  
- Data directories → `data/raw`, `data/interim`, `data/processed`  
- Outputs → `results/runs/`  
- Logs and metadata → `results/runs/<run_id>/logs/`, `metadata.json`  

This document ensures that:
- execution is reproducible  
- processing steps are traceable  
- documentation reflects actual implementation  

Each pipeline stage receives and updates a shared `state` object, allowing data to be passed sequentially between stages without reliance on global variables or implicit dependencies.

---

## 1. Purpose

This pipeline performs **variant interpretation and annotation** on genomic variant data.

Objective:
- Transform raw variant calls into structured, annotated, and prioritized outputs suitable for downstream analysis or clinical review.

Input:
- Variant Call Format (VCF) file

Output:
- Annotated and filtered variant table
- Summary report of prioritized variants

This workflow reflects the core structure of pipelines used in:
- clinical genomics
- variant curation
- molecular diagnostics

---

## 2. Scope

This SOP applies to:

- Small-scale variant datasets (single-sample or small cohort)
- Human genomic data (GRCh38 assumed)
- Local execution on a workstation

This SOP does NOT cover:

- Joint genotyping workflows  
- Structural variant analysis  
- Large-scale cohort processing  
- Production-grade clinical validation  

---

## 3. Inputs

### 3.1 Primary Data
- VCF file containing variant calls

Example:

`data/raw/example_variants.vcf`


### 3.2 Reference Data
- Gene annotation mapping (toy dataset for Version 1)
- Optional: mock clinical annotations

### 3.3 Metadata
- Sample identifier  
- Run parameters from configuration  

### Repository Mapping
- Input path defined in `config/config.yaml`  
- Raw data stored in `data/raw/`  

---

## 4. Outputs

### 4.1 Intermediate Outputs
- Parsed variant table  
- Cleaned and normalized variant dataset  

### 4.2 Final Outputs
- Annotated variant table  
- Filtered/prioritized variant list  

### 4.3 QC Outputs
- Variant counts before/after filtering  
- Annotation completeness metrics  

### Repository Mapping
- Interim data → `data/interim/`  
- Processed data → `data/processed/`  
- Final outputs → `results/runs/<run_id>/final/`  
- Reports → `results/runs/<run_id>/reports/`  

---

## 5. Software and Environment

| Tool    | Purpose                     |
|--------|----------------------------|
| Python | Pipeline execution         |
| pandas | Data processing           |

### Environment
- OS: Linux (Pop!_OS)  
- Execution: local workstation  
- Dependencies: defined in `requirements.txt`  

### Repository Mapping
- Dependencies → `requirements.txt`  
- Runtime info → `metadata.json`  

---

## 6. Pipeline Overview

Workflow:

`VCF → Parsing → Validation → Cleaning → Annotation → Filtering → Reporting`

### Repository Mapping
- Entry point → `run_pipeline.py`  
- Orchestration → `src/pipeline_runner.py`  

---

### 6.1 Data Flow and State Management

Data flows sequentially through pipeline stages using both:

- explicit file outputs (interim and processed data)
- an in-memory `state` object passed between stages

This hybrid approach ensures:
- reproducibility through persisted files
- efficiency through in-memory data passing
- clarity of stage dependencies

---

## 7. Detailed Procedure

Each stage includes explicit QC checks to ensure data integrity before proceeding to downstream steps.

---

### Step 1 — Load Variant Data

**Module:** `pipeline/stage_01_load_data.py`

**Input:**
- VCF file

**Description:**
- Parse VCF into tabular format

**Rationale:**
- Convert raw variant data into structured representation

**QC:**
- File exists  
- Non-zero variant count  
- Fields correctly parsed  

---

### Step 2 — Validate Variant Data

**Module:** `pipeline/stage_02_validate_data.py`

**Input:**
- Parsed variant table

**Description:**
- Validate schema integrity and required fields:
  - chromosome
  - position
  - reference allele
  - alternate allele

**Rationale:**
- Ensure downstream processing integrity

**QC:**
- Required columns present  
- No critical null values  

---

### Step 3 — Clean and Normalize Data

**Module:** `pipeline/stage_03_clean_data.py`

**Input:**
- Validated variant data

**Description:**
- Normalize chromosome naming  
- Remove malformed entries  
- Standardize formats  

**Rationale:**
- Ensure consistent representation for annotation  

**QC:**
- Row counts before/after cleaning  
- No invalid records remain  

**Output Location:**
- `data/interim/`

---

### Step 4 — Annotate Variants

**Module:** `pipeline/stage_04_transform_data.py`

**Input:**
- Cleaned variant dataset

**Description:**
- Add:
  - gene symbol  
  - variant consequence  
  - placeholder annotation fields (Version 1 demonstration only)  

**Rationale:**
- Provide biological context  

**QC:**
- Annotation completeness  
- Presence of gene labels  

**Output Location:**
- `data/processed/`

---

### Step 5 — Filter and Prioritize Variants

**Module:** `pipeline/stage_05_analyze_data.py`

**Input:**
- Annotated variant dataset

**Description:**
Apply filtering criteria, for example:
- protein-coding variants
- predicted high-impact consequences (e.g., nonsense, frameshift)
- variants with annotation data present

**Rationale:**
- Reduce to biologically relevant candidates  

**QC:**
- Variant count reduction  
- Output not empty  

**Output Location:**
- `results/runs/<run_id>/final/`

---

### Step 6 — Generate Reports

**Module:** `pipeline/stage_06_write_summary.py`

**Input:**
- Filtered variant dataset

**Description:**
- Generate summary outputs:
  - variant table  
  - counts  
  - simple report  

**Rationale:**
- Provide human-readable results  

**QC:**
- Output files exist  
- Formatting is correct  

**Output Location:**
- `results/runs/<run_id>/reports/`

---

## 8. Interpretation

Variants are interpreted based on:

- gene association  
- predicted functional consequence  
- annotation fields  

Example:
- high-impact variants prioritized  
- gene-level grouping performed  

Note:
This pipeline uses simplified annotation logic for demonstration.

Interpretation prioritizes variants based on predicted functional impact and gene-level relevance.

---

## 9. Assumptions

- Input VCF is well-formed  
- Annotation reference is accurate  
- Dataset size is manageable locally  

---

## 10. Limitations

- No real annotation database (e.g., ClinVar, gnomAD)  
- No population frequency filtering  
- No structural variant support  
- Not clinically validated  

This pipeline is intended for demonstration and development purposes, not clinical deployment.

---

## 11. Reproducibility

Reproducibility is ensured by:

- configuration-driven execution  
- config snapshot saved per run  
- metadata tracking  
- structured output directories  

### Repository Mapping
- Config snapshot → `results/runs/<run_id>/config_used.yaml`  
- Metadata → `results/runs/<run_id>/metadata.json`  

Each run directory is self-contained and sufficient to reproduce results independently.

---

## 12. Logging and Traceability

Each run produces:

- pipeline log file  
- execution trace  
- metadata record  

### Repository Mapping
- Logs → `results/runs/<run_id>/logs/pipeline.log`  

All major pipeline events (stage start, completion, and errors) are recorded in the pipeline log.

---

## 13. Future Extensions

- Integrate real annotation tools (VEP, ANNOVAR)  
- Add population frequency filtering  
- Incorporate ClinVar and OMIM  
- Expand to cohort-level analysis  
- Enable database integration  

---

# End of SOP Example
