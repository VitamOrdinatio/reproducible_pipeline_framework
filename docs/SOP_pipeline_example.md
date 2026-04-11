# SOP Pipeline Example  
## Variant Interpretation / Annotation Pipeline (Framework Demonstration)

---

# 0. Relationship to Pipeline Implementation

This SOP is a concrete example of how the SOP template maps directly to a working pipeline.

Each step in this SOP corresponds to:

- Pipeline modules → `pipeline/stage_*.py`
- Configuration → `config/config.yaml`
- Data directories → `data/raw`, `data/interim`, `data/processed`
- Outputs → `results/runs/`
- Logs and metadata → `logs/`, `metadata.json`

This document demonstrates how a real pipeline is implemented using the reproducible pipeline framework.

---

# 1. Purpose

This pipeline performs **variant interpretation and annotation** on genomic variant data.

- Input: Variant Call Format (VCF) file
- Goal: Annotate, filter, and prioritize variants
- Output: Structured variant table and summary report

This example simulates a clinical genomics workflow relevant to:
- variant curation
- annotation pipelines
- clinical reporting environments

---

# 2. Scope

This SOP applies to:

- Small to moderate VCF datasets
- Human genomic data (GRCh38 assumed)
- Local execution on a workstation

This SOP does NOT cover:

- Joint genotyping
- Structural variants
- Large cohort scaling
- Production clinical pipelines

---

# 3. Inputs

## 3.1 Primary Data
- Input VCF file

Example:
data/raw/example_variants.vcf

---


## 3.2 Reference Data
- Gene annotation reference (simplified toy mapping)
- Optional: ClinVar-like annotations (toy dataset)

## 3.3 Metadata
- Sample identifier
- Pipeline version
- Run configuration

## Repository Mapping
- Input file path → `config/config.yaml`
- Raw data → `data/raw/`
- Example data → `data/example/`

---

# 4. Outputs

## 4.1 Intermediate Outputs
- Parsed variant table
- Annotated intermediate dataset

## 4.2 Final Outputs
- Filtered variant table
- Prioritized variant list
- Summary report

## 4.3 QC Outputs
- Variant counts before/after filtering
- Annotation completeness metrics

## Repository Mapping
- Interim data → `data/interim/`
- Processed data → `data/processed/`
- Final outputs → `results/runs/<run_id>/final/`
- Reports → `results/runs/<run_id>/reports/`

---

# 5. Software and Environment

| Tool | Version | Purpose |
|------|--------|--------|
| Python | 3.x | Core pipeline execution |
| pandas | X.X | Data processing |
| custom scripts | N/A | Parsing, annotation, filtering |

## Environment
- OS: Linux (Pop!_OS)
- Execution: local workstation
- Dependencies: `requirements.txt`

## Repository Mapping
- Dependencies → `requirements.txt`
- Environment notes → `environment/README.md`
- Runtime capture → `metadata.json`

---

# 6. Pipeline Overview

High-level workflow:

VCF → Parsing → Validation → Annotation → Filtering → Reporting

## Repository Mapping
- Entry point → `run_pipeline.py`
- Orchestration → `src/pipeline_runner.py`
- Documentation → `docs/workflow.md`

---

# 7. Detailed Procedure

---

## Step 1 — Load VCF Data

### Input:
- VCF file

### Description:
Parse VCF into tabular format.

### Rationale:
Convert raw variant data into structured form.

### QC:
- File exists
- Non-zero variants
- Correct parsing of fields

### Repository Mapping:
- Module → `pipeline/stage_01_load_data.py`

---

## Step 2 — Validate Variant Data

### Input:
- Parsed variant table

### Description:
Ensure required fields exist:
- chromosome
- position
- reference allele
- alternate allele

### Rationale:
Prevent downstream errors.

### QC:
- Missing columns
- Null values
- Format consistency

### Repository Mapping:
- Module → `pipeline/stage_02_validate_data.py`
- Validation scripts → `scripts/validation/`

---

## Step 3 — Clean and Normalize Data

### Input:
- Validated variant data

### Description:
- Normalize chromosome naming
- Remove malformed entries
- Standardize fields

### Rationale:
Ensure consistency for annotation.

### QC:
- Row counts before/after cleaning
- No malformed entries

### Repository Mapping:
- Module → `pipeline/stage_03_clean_data.py`
- Output → `data/interim/`

---

## Step 4 — Annotate Variants

### Input:
- Cleaned variant table

### Description:
Add:
- gene symbol
- variant consequence (missense, nonsense, etc.)
- mock clinical annotation

### Rationale:
Provide biological context to variants.

### QC:
- Annotation completeness
- Presence of gene labels

### Repository Mapping:
- Module → `pipeline/stage_04_transform_data.py`
- Output → `data/processed/`

---

## Step 5 — Filter and Prioritize Variants

### Input:
- Annotated variants

### Criteria:
- Coding variants
- High-impact variants
- Clinically relevant annotations

### Rationale:
Reduce variant set to meaningful candidates.

### QC:
- Variant count reduction
- No empty outputs

### Repository Mapping:
- Module → `pipeline/stage_05_analyze_data.py`
- Output → `results/runs/<run_id>/final/`

---

## Step 6 — Generate Reports

### Input:
- Filtered variants

### Description:
Generate:
- summary table
- variant counts
- report file

### Rationale:
Provide human-readable output.

### QC:
- File existence
- Correct formatting

### Repository Mapping:
- Module → `pipeline/stage_06_write_summary.py`
- Output → `results/runs/<run_id>/reports/`

---

# 8. Biological Interpretation

Variants are interpreted based on:

- gene association
- predicted functional consequence
- mock clinical annotation

Example:
- missense variants in POLG prioritized
- nonsense variants flagged as high impact

Note:
This example uses simplified annotation logic for demonstration purposes.

---

# 9. Assumptions

- VCF is correctly formatted
- Reference annotation is accurate
- Toy dataset represents real-world structure

## Repository Mapping
- Documented in `docs/notes.md`
- Encoded in config parameters

---

# 10. Limitations

- Simplified annotation (not real ClinVar)
- No population frequency filtering
- No structural variants
- Not clinically validated

## Repository Mapping
- `docs/notes.md`
- `docs/roadmap.md`

---

# 11. Reproducibility

Reproducibility is ensured through:

- config-driven execution
- config snapshot saved per run
- metadata capture
- structured run directories

## Repository Mapping
- Config snapshot → `results/runs/*/config_used.yaml`
- Metadata → `results/runs/*/metadata.json`
- Execution → `run_pipeline.py`

---

# 12. Logging and Traceability

Each run produces:

- pipeline log file
- stage execution logs
- metadata file
- timestamped run directory

## Repository Mapping
- Logs → `results/runs/*/logs/pipeline.log`
- Metadata → `metadata.json`
- Run directories → `results/runs/run_*`

---

# 13. Future Extensions

- Integrate real annotation tools (ANNOVAR, VEP)
- Add population frequency filtering (gnomAD)
- Incorporate ClinVar and OMIM
- Expand to cohort analysis
- Add database integration
- Enable scalable execution

## Repository Mapping
- `docs/roadmap.md`

---

# End of SOP Example