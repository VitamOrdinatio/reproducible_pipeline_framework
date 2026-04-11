# Standard Operating Procedure (SOP) Template  
## Reproducible Computational / Bioinformatics Pipeline

---

# 0. Relationship to Pipeline Implementation

This SOP is not only a narrative document — it is intended to map directly to the repository structure and pipeline implementation.

Each section of this SOP should correspond to:

- **Pipeline modules** → `pipeline/stage_*.py`
- **Configuration parameters** → `config/config.yaml`
- **Data directories** → `data/raw`, `data/interim`, `data/processed`
- **Results outputs** → `results/` or `results/runs/`
- **Logs and metadata** → `logs/`, `metadata.json`

The goal is to ensure that:
- documentation reflects actual execution
- pipelines are reproducible and traceable
- each procedural step has a concrete implementation

---

# 1. Purpose

Describe the objective of this pipeline.

- What biological or computational question is being addressed?
- What type of data is being processed (e.g., FASTQ, CSV, TSV, database exports)?
- What is the intended outcome (e.g., variant discovery, expression analysis, harmonized dataset, ranked gene list)?

---

# 2. Scope

Define the boundaries of this SOP.

- What data types are supported?
- What organisms, systems, or domains are assumed (if applicable)?
- What is explicitly NOT covered?

---

# 3. Inputs

List all required inputs.

## 3.1 Primary Data
- Raw input data (e.g., FASTQ, CSV, TSV, JSON, database dump)
- Source (SRA / GEO / local / API / database export)

## 3.2 Reference Data (if applicable)
- Reference genome (e.g., GRCh38)
- Annotation files (e.g., GTF, BED)
- External datasets (e.g., ClinVar, gnomAD, MitoCarta)

## 3.3 Metadata
- Sample identifiers
- Experimental conditions
- Clinical or phenotypic metadata (if applicable)

## Repository Mapping
- Config paths → `config/config.yaml`
- Input files → `data/raw/` or external storage
- Schema expectations → `docs/data_schema.md`

---

# 4. Outputs

Define expected outputs.

## 4.1 Intermediate Outputs
- Partially processed data
- Temporary or staged files (e.g., cleaned tables, aligned reads)

## 4.2 Final Outputs
- Final datasets (e.g., processed tables, VCFs, expression matrices)
- Reports or summaries
- Database tables (if applicable)

## 4.3 QC Outputs
- Validation reports
- Summary statistics
- Data quality metrics

## Repository Mapping
- Intermediate data → `data/interim/`
- Processed data → `data/processed/`
- Final outputs → `results/` or `results/runs/`
- Reports → `results/reports/` or `results/tables/`

---

# 5. Software and Environment

List all tools and versions used.

| Tool | Version | Purpose |
|------|--------|--------|
| Tool 1 | X.X | Description |
| Tool 2 | X.X | Description |

## Environment
- OS (e.g., Linux, Pop!_OS)
- Hardware constraints (CPU, RAM)
- Python version / environment
- Dependencies (`requirements.txt` or `environment.yml`)

## Repository Mapping
- Environment documentation → `environment/README.md`
- Dependencies → `requirements.txt`
- Runtime capture → `metadata.json`

---

# 6. Pipeline Overview

Provide a high-level summary of the workflow.

General pattern:
Input Data → Validation → Cleaning → Transformation → Analysis → Outputs → QC

Optional example (sequencing):
FASTQ → Alignment → BAM → QC → Variant Calling → Annotation

## Repository Mapping
- Execution flow → `run_pipeline.py`
- Orchestration → `src/pipeline_runner.py`
- Documentation → `docs/workflow.md`

---

# 7. Detailed Procedure

Each step should correspond to a pipeline stage module.

---

## Step 1 — Data Acquisition / Loading

### Input:
- Raw input data

### Description:
Load or retrieve data from source.

### Rationale:
Ensure data is available for processing.

### QC:
- File existence
- File integrity (size, checksum optional)

### Repository Mapping:
- Module → `pipeline/stage_01_load_data.py`

---

## Step 2 — Input Validation

### Input:
- Raw data

### Description:
Validate schema, required columns, and data integrity.

### Rationale:
Prevent downstream errors.

### QC:
- Column presence
- Data types
- Missing values

### Repository Mapping:
- Module → `pipeline/stage_02_validate_data.py`
- Validation scripts → `scripts/validation/`

---

## Step 3 — Data Cleaning / Preprocessing

### Input:
- Raw or validated data

### Description:
Handle missing values, normalize formats, remove inconsistencies.

### Rationale:
Prepare data for transformation and analysis.

### QC:
- Row counts before/after
- Missing value handling

### Repository Mapping:
- Module → `pipeline/stage_03_clean_data.py`
- Outputs → `data/interim/`

---

## Step 4 — Data Transformation

### Input:
- Cleaned data

### Description:
Transform data into analysis-ready format.

### Rationale:
Standardize structure for downstream processing.

### QC:
- Field correctness
- Derived values validation

### Repository Mapping:
- Module → `pipeline/stage_04_transform_data.py`
- Outputs → `data/processed/`

---

## Step 5 — Analysis

### Input:
- Processed data

### Description:
Perform analysis, computation, or scoring.

### Rationale:
Generate meaningful results.

### QC:
- Sanity checks on outputs
- Expected value ranges

### Repository Mapping:
- Module → `pipeline/stage_05_analyze_data.py`
- Outputs → `results/`

---

## Step 6 — Output Generation and Reporting

### Input:
- Analysis results

### Description:
Write final outputs and reports.

### Rationale:
Produce human-readable and machine-readable outputs.

### QC:
- Output completeness
- File existence
- Summary statistics

### Repository Mapping:
- Module → `pipeline/stage_06_write_summary.py`
- Outputs → `results/`, `results/tables/`, `results/figures/`

---

# 8. Biological or Analytical Interpretation

Describe how results are interpreted.

- Gene-level or feature-level interpretation
- Functional consequences (if applicable)
- Domain-specific insights
- Clinical or biological relevance

Note:
This section is pipeline-specific and may be minimal for infrastructure repositories.

---

# 9. Assumptions

List assumptions made during analysis.

- Data quality assumptions
- Reference data accuracy
- Tool default behavior

## Repository Mapping
- Documented in `docs/notes.md`
- Encoded in `config/config.yaml`

---

# 10. Limitations

Describe known limitations.

- Data limitations
- Methodological constraints
- Potential biases
- False positive / negative risks

## Repository Mapping
- `docs/notes.md`
- `docs/roadmap.md`

---

# 11. Reproducibility

Ensure reproducibility by documenting:

- Software versions
- Parameters used
- Input data sources
- Config file used
- Pipeline version

## Repository Mapping
- Config snapshot → `results/runs/*/config_used.yaml`
- Metadata → `results/runs/*/metadata.json`
- Pipeline execution → `run_pipeline.py`

---

# 12. Logging and Traceability

Describe how runs are tracked.

- Log files
- Output directories
- Run identifiers
- Execution timestamps

## Repository Mapping
- Logs → `results/runs/*/logs/`
- Metadata → `metadata.json`
- Run directories → `results/runs/run_YYYY_MM_DD_HHMMSS/`

---

# 13. Future Extensions

Optional improvements:

- Additional QC metrics
- Expanded annotation or datasets
- Database integration
- Scaling to larger datasets
- Parallelization or HPC execution

## Repository Mapping
- `docs/roadmap.md`

---

# End of SOP