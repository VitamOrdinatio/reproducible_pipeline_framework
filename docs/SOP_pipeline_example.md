# Standard Operating Procedure (SOP) Pipeline Example 
## Variant Discovery and Dual-Track Annotation Pipeline

This SOP provides a concrete example of how the reproducible pipeline framework can be instantiated for a genomics variant discovery and annotation workflow. It is intentionally domain-specific and demonstrates the integration of sequencing data processing, variant annotation, and dual-track prioritization. This document should be used as a reference implementation and adapted as needed for other pipeline types (e.g., RNA-seq, database construction, or clinical harmonization), rather than copied verbatim.

---

# 0. Relationship to Pipeline Implementation

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

### Step vs Stage Terminology

In this document:

- **Steps** refer to conceptual pipeline operations described in the SOP.
- **Stages** refer to concrete implementation units within the codebase.

Mapping:

- Each **Step N** corresponds directly to **Stage N** implemented as:
  `pipeline/stage_NN_<name>.py`

Example:
- Step 1 — Data Acquisition → `stage_01_load_data.py`
- Step 2 — Alignment → `stage_02_align_data.py`

This distinction ensures that:
- the SOP remains human-readable
- the implementation remains modular and executable

---

# 1. Purpose

This pipeline identifies, annotates, and prioritizes genomic variants from sequencing data, supporting both coding and non-coding variant interpretation using classical bioinformatics and modern AI-based prediction tools.

This pipeline performs end-to-end variant discovery, annotation, and prioritization.

Pipeline Layering:
`DATA → PROCESSING → ANNOTATION → FILTER/PARTITION → INTERPRET → VALIDATE`

Primary Input:
- FASTQ (full pipeline)

Optional Input:
- VCF (annotation-only mode)

Output:
- Annotated and filtered variant table
- Summary report of prioritized variants

Objective:
- Transform raw variant calls into structured, annotated, and prioritized outputs suitable for downstream analysis or clinical review.

This workflow reflects the core structure of pipelines used in:
- clinical genomics
- variant curation
- molecular diagnostics

---

# 2. Scope

This SOP supports:

- Whole Exome Sequencing (WES)
- Whole Genome Sequencing (WGS) (GRCh38 assumed)
- Small-scale variant datasets (single-sample or small cohort)
- Local execution on a workstation

This SOP includes:

- Coding variant interpretation
- Non-coding variant prioritization

This SOP does NOT cover:

- Joint genotyping workflows  
- Structural variant discovery
- Structural variant analysis  
- Large-scale cohort processing  
- Production-grade clinical validation  
- Clinical reporting workflows

---

# 3. Inputs

## 3.1 Primary Data

- FASTQ files (paired-end preferred)

Example:

`data/raw/example_NGS_WGS.fastq`

## 3.2 Reference Data

- Reference genome (e.g., GRCh38)
- Annotation databases (RefSeq / Ensembl)

## 3.3 Metadata

- Sample identifier  
- Run parameters from configuration  

## 3.4 Repository Mapping

- Input path defined in `config/config.yaml`  
- Raw data stored in `data/raw/`  

## 3.5 Annotation Resources

- gnomAD (primary AF)
- ExAC (optional legacy AF)
- 1000 Genomes (optional AF)
- ClinVar
- AlphaMissense (precomputed)
- SpliceAI (precomputed or local)

## 3.6 Optional Resources
- AlphaGenome (API-based, optional)

---

# 4. Outputs

## 4.1 Intermediate

- BAM (sorted, indexed)
- QC reports

## 4.2 Final Outputs

- VCF
- annotated_variants.tsv
- prioritized_variants.tsv

## 4.3 QC Outputs

- Variant counts before/after filtering  
- Annotation completeness metrics  

### 4.4 Repository Mapping

- Interim data → `data/interim/`  
- Processed data → `data/processed/`  
- Final outputs → `results/runs/<run_id>/final/`  
- Reports → `results/runs/<run_id>/reports/` 

---

# 5. Software and Environment

| Tool          | Purpose                                |
|---------------|----------------------------------------|
| Python        | Pipeline execution                     |
| pandas        | Tabular data processing                |
| BWA-MEM       | Read alignment                         |
| samtools      | BAM processing and QC                  |
| GATK          | Variant calling and VCF normalization  |
| ANNOVAR       | Variant annotation                     |
| IGV           | Manual read-level validation           |
| AlphaMissense | Coding missense prioritization         |
| SpliceAI      | Splice effect prediction               |
| AlphaGenome   | Optional, API-based                    |

## 5.1 Environment

- OS: Linux (Pop!_OS)  
- Execution: local workstation  
- Dependencies: defined in `requirements.txt`  

## 5.2 Repository Mapping

- Dependencies → `requirements.txt`  
- Runtime info → `metadata.json`  

---

# 6. Pipeline Overview

## 6.1 Workflow:

`FASTQ → BAM → QC → VCF → Annotation → Dual-Track Interpretation → Validation`

## 6.2 Data Flow and State Management

Data flows sequentially through pipeline stages using both:

- explicit file outputs (interim and processed data)
- an in-memory `state` object passed between stages

This hybrid approach ensures:
- reproducibility through persisted files
- efficiency through in-memory data passing
- clarity of stage dependencies

## 6.3 Repository Mapping

- Entry point → `run_pipeline.py`  
- Orchestration → `src/pipeline_runner.py`  

---

# 7. Detailed Procedure

Each stage includes explicit QC checks to ensure data integrity before proceeding to downstream steps.

---

### Step 1 — Data Acquisition — Load Sequencing Data

**Module:** `pipeline/stage_01_load_data.py`

**Description:**
- Load raw reads in FASTQ format

**Rationale:**
- Load raw sequencing data in preparation for downstream structured transformations

**Input:**
- FASTQ

**Output:**
- validated FASTQ input path(s)
- initialized sample context in state

**QC:**
- file exists
- FASTQ format is valid
- file integrity check (e.g., checksum or read count sanity)

---

### Step 2 — Alignment

**Module:** `pipeline/stage_02_align_data.py`

**Description:**
- Align and map raw reads to a reference genome (e.g. GRCh38).

**Rationale:**
- Mapping raw NGS reads onto a reference genome is critical for subsequent subsetting and variant calling.

**Input:**
- FASTQ

**Tool:**
- BWA-MEM

**Output:**
- BAM

**QC:**
- alignment completed successfully
- BAM file created
- mapping rate available

---

### Step 3 — BAM Processing

**Module:** `pipeline/stage_03_process_BAM.py`

**Description:**
- Sort and index mapped reads.

**Rationale:**
- Sorting and indexing mapped reads into a structured format is required for downstream variant call and annotation functions.

**Input:**
- BAM

**Tool:**
- samtools

**Actions:**
- Sort BAM
- Index BAM

**Output:**
- sorted BAM
- BAI (BAM index file)

**QC:**
- BAM sorting completed
- BAM index created successfully
- read counts preserved after sorting

---

### Step 4 — Quality Control

**Module:** `pipeline/stage_04_QC_aligned_reads.py`

**Description:**
- Obtain the summary stats of mapped reads

**Rationale:**
- Get number of mapped reads, duplication rates, and coverage estimates for a baseline understanding of sample QC.

**Input:**
- BAM
- BAI

**Tool:**
- samtools flagstat
- samtools stats
- samtools idxstats

**Output:**
- total reads
- mapped reads
- duplication (if available)

**QC:**
- flagstat/stats/idxstats completed successfully
- mapped read summary recorded
- coverage metrics recorded if available

---

### Step 5 — Variant Calling

**Module:** `pipeline/stage_05_call_variants.py`

**Description:**
- Perform variant calling in a variant discovery layer.

**Rationale:**
- Execute GATK for variant calling to generate local haplotypes, generate local assembly, and call SNPs and indel polymorphisms.

**Input:**
- clean BAM

**Tool:**
- GATK HaplotypeCaller

**Actions:**
- Generate local haplotypes
- Generate local assembly
- Call SNP variants
- Call indel variants

**Output:**
- VCF

**QC:**
- VCF file generated successfully
- Variant count recorded
- No malformed records detected

---

### Step 6 — VCF Normalization and Cleaning

**Module:** `pipeline/stage_06_normalize_VCF.py`

**Description:**
- Separate noise from true biological variation  

**Rationale:**
- Ensure consistent representation for annotation  

**Input:**
- VCF

**Tool:**
- GATK

**Actions:**
- Normalize chromosome naming  
- Remove malformed entries  
- Standardize formats  

**Output:**
- normalized VCF (data/interim/normalized.vcf)

**QC:**
- normalized VCF created
- malformed records removed or flagged
- VCF format validated

---

### Step 7 — Annotation (NO FILTERING)

**Module:** `pipeline/stage_07_annotate_variants.py`

**Description:**
- Annotate discovered variants.

**Rationale:**
- Variants come in all forms and sizes and annotation provides biological meaning and clinical understanding.

**Input:**
- normalized VCF

**Tools:**
- ANNOVAR (biological meaning)
- gnomAD (allele frequency, AF)
- ExAC (allele frequency, AF)
- 1000 Genomes (allele frequency, AF)
- HGMD (optional; subscription-based)
- ClinVar (clinical consensus regarding variant and disease)

**Actions:**
- obtain molecular biological context for variants (ANNOVAR)
- retrieve allele frequency annotations from gnomAD, ExAC, and 1000 Genomes
- get evidence of prior variant pathogenicity in literature (HGMD)
- get clinical consensus regarding variant pathogenicity (ClinVar)

**Output:**
- annotated VCF
- annotated variant table

**Output Location:**
- `data/processed/`

**QC:**
- annotation completed successfully
- required annotation fields present
- annotation completeness metrics recorded

#### Annotation Types:

##### Structural / Functional

- Gene name
- Variant type (missense, nonsense, intronic, intergenic)
- Protein change

##### Population Frequency

- AF_gnomAD
- AF_ExAC
- AF_1KGenomes

##### Clinical Annotation

- ClinVar classification

##### AI-Based Annotation (CORE)

- AlphaMissense_score (for missense variants)
- SpliceAI_score (for splice-relevant variants)

##### Variant Classification Field

- Variant_Type = {coding, non-coding}

### IMPORTANT PRINCIPLE

No variants are removed at this stage.

Annotation adds information; it does not filter variants.

---

### Step 8 — Global Filtering and Partitioning into Dual Tracks

**Module:** `pipeline/stage_08_filter_and_partition.py`

**Actions:**
- Remove variants with high AF (threshold depends on disease model)
- Apply AF filtering using thresholds defined in config/config.yaml
- Thresholds are configurable per run and may differ for coding vs non-coding variants.
- Partition remaining variants into:
    - coding (track A)
    - non-coding (track B)

Variants are separated into:

#### Track A — Coding Variants
- missense
- nonsense
- frameshift
- splice-site

#### Track B — Non-Coding Variants
- intronic
- intergenic
- regulatory regions

---

### Step 9 — Interpretation (Track A: Coding)

**Module:** `pipeline/stage_09_interpret_coding.py`

#### Evidence Integration
- ClinVar (primary)
- AlphaMissense (functional support)
- SpliceAI (if near exon boundary)

#### Interpretation Logic
- Rare + damaging → prioritize
- Known pathogenic → prioritize
- VUS → consider AI support

---

### Step 10 — Interpretation (Track B: Non-Coding)

**Module:** `pipeline/stage_10_interpret_noncoding.py`

#### Evidence Integration
- Limited ClinVar signal expected
- SpliceAI (if splice-relevant)

#### AI-Based Prioritization
AlphaGenome (OPTIONAL; applied only to prioritized non-coding or VUS candidate variants)

AlphaGenome is treated as an external or API-based dependency and is not required for core pipeline execution.

Used for:
- regulatory disruption
- expression changes
- chromatin effects

---

### IMPORTANT PRINCIPLE

`AlphaGenome is applied selectively to high-priority non-coding or VUS variants only.`

---

### Step 11 — Variant Prioritization

**Module:** `pipeline/stage_11_prioritize_variants.py`

**Input:**
- interpreted coding-track table
- interpreted non-coding-track table

Combine all evidence:

Priority score considers:

- rarity (gnomAD, 1000 Genomes, ExAC)
- functional impact (ANNOVAR)
- clinical evidence (ClinVar)
- AlphaMissense (coding)
- SpliceAI (splice)
- AlphaGenome (non-coding / optional)

---

### Step 12 — Validation

**Module:** `pipeline/stage_12_validate_variants.py`

Tool:
- IGV

Validate:
- read depth
- allele balance
- strand bias
- alignment artifacts

---

### Step 13 — Generate Reports

**Module:** `pipeline/stage_13_write_summary.py`

**Input:**
- prioritized variant table
- QC summaries
- annotation summary
- prioritization summary
- validation summary (if available)

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

# 8. Biological Interpretation

Interpret variants in context of:

- gene function (e.g., POLG)
- domain location (NTD vs CTD)
- inheritance model (dominant vs recessive)
- penetrance considerations

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

# 9. Assumptions

- Reference genome is accurate
- Sequencing quality sufficient
- Annotation databases up-to-date
- Dataset size is manageable locally  

---

# 10. Limitations

- WES may miss regulatory variants
- Non-coding interpretation remains uncertain
- AI predictions are probabilistic, not definitive
- No structural variant support  
- Not clinically validated  

This pipeline is intended for demonstration and development purposes, not clinical deployment.

---

# 11. Reproducibility

Reproducibility is ensured by:

- configuration-driven execution  
- config snapshot saved per run  
- metadata tracking  
- structured output directories 

## Repository Mapping
- Config snapshot → `results/runs/<run_id>/config_used.yaml`  
- Metadata → `results/runs/<run_id>/metadata.json`  

Each run directory is self-contained and sufficient to reproduce results independently.

---

# 12. Logging

Each run produces:

- pipeline log file  
- execution trace  
- metadata record  

## Repository Mapping
- Logs → `results/runs/<run_id>/logs/pipeline.log`  

All major pipeline events (stage start, completion, and errors) are recorded in the pipeline log.

---

# 13. Future Extensions


- Integrate additional annotation tools (VEP)  
- Incorporate OMIM
- Incorporate HGMD for population frequency filtering (currently HGMD is optional; subscription-based)
- Expand to cohort-level analysis  
- Enable database integration
- Improve regulatory annotation
- Add structural variant detection

---

# 14. Final Conceptual Model

Workflow:

`DATA → PROCESSING → ANNOTATION → PARTITION → INTERPRETATION → VALIDATION`

Handling coding variants:

`Coding variants: ClinVar + AlphaMissense + SpliceAI`

Handling non-coding variants:

`Non-coding variants: SpliceAI + AlphaGenome (optional)`

---

# 15. State Object Contract

Each pipeline stage receives a shared `state` object and returns an updated `state` object.

The purpose of the `state` object is to provide a single, explicit, traceable record of pipeline execution without relying on global variables or implicit dependencies.

### The `state` object stores:

- run metadata
- configuration values
- sample metadata
- file paths produced by prior stages
- QC summaries
- annotation metadata
- track-specific outputs
- prioritization outputs
- validation targets
- log paths
- warnings and errors

### Design Principles

1. The `state` object should be serializable.
2. The `state` object should prefer file paths over large in-memory payloads.
3. Each stage should read only the keys it requires and write only the keys it produces.
4. Missing required keys should cause a clear failure with explicit error logging.
5. Large artifacts such as FASTQ, BAM, and VCF files should be persisted to disk and referenced in `state` by path.
6. The `state` object should support both:
   - full-pipeline mode (FASTQ → BAM → VCF → annotation → prioritization)
   - annotation-only mode (VCF input)

### Typical Contents of `state`

Examples of information expected in `state` include:

- `run_id`
- execution mode
- sample identifier
- input FASTQ path(s)
- input VCF path (if annotation-only mode)
- aligned BAM path
- sorted BAM path
- BAM index path
- raw VCF path
- normalized VCF path
- annotated variant table path
- coding-track table path
- non-coding-track table path
- prioritized variant table path
- summary report path
- QC summaries
- annotation resources used
- validation candidate list
- pipeline log path
- warnings
- errors

### Stage Behavior

Each stage should:

- validate that required `state` keys are present before execution
- perform its assigned transformation or analysis
- update `state` with newly created outputs, summaries, and metadata
- record any warnings or errors in a consistent location

### Reproducibility Rule

The `state` object should function as a compact execution record.

In general:

- metadata, paths, summaries, warnings, and errors belong in `state`
- large data artifacts belong on disk

This design ensures that the pipeline remains reproducible, debuggable, and easy to bind to concrete pipeline modules.

# 16. Stage Read/Write Contract

Each pipeline stage must declare, either explicitly in code or implicitly through implementation structure:

- required inputs from `state`
- outputs written back to `state`
- files created on disk
- QC summaries produced
- warnings or errors generated

This contract ensures that stage boundaries are explicit and that pipeline execution remains traceable and reproducible.

---

### General Rule

For every stage:

- read only the keys required for execution
- write only the keys produced by that stage
- fail clearly if required inputs are missing
- record file paths rather than large data objects whenever possible

---

### Stage 1 — Data Acquisition

**Reads from `state`:**
- configuration values
- input FASTQ path(s) OR input VCF path (annotation-only mode)

**Writes to `state`:**
- sample metadata
- validated input file paths
- FASTQ QC summary
- execution mode confirmation

**Files created on disk:**
- none required

---

### Stage 2 — Alignment

**Reads from `state`:**
- input FASTQ path(s)
- reference genome path
- run configuration

**Writes to `state`:**
- aligned BAM path
- alignment QC summary

**Files created on disk:**
- aligned BAM

---

### Stage 3 — BAM Processing

**Reads from `state`:**
- aligned BAM path

**Writes to `state`:**
- sorted BAM path
- BAM index path
- BAM processing QC summary

**Files created on disk:**
- sorted BAM
- BAM index (`.bai`)

---

### Stage 4 — Quality Control

**Reads from `state`:**
- sorted BAM path
- BAM index path

**Writes to `state`:**
- read count summary
- mapping summary
- duplication summary (if available)
- coverage summary (if available)

**Files created on disk:**
- QC report files

---

### Stage 5 — Variant Calling

**Reads from `state`:**
- sorted BAM path
- BAM index path
- reference genome path

**Writes to `state`:**
- raw VCF path
- variant calling summary
- raw variant count

**Files created on disk:**
- raw VCF

---

### Stage 6 — VCF Normalization and Cleaning

**Reads from `state`:**
- raw VCF path

**Writes to `state`:**
- normalized VCF path
- VCF normalization summary
- normalized variant count
- VCF format validation result

**Files created on disk:**
- normalized VCF

---

### Stage 7 — Annotation

**Reads from `state`:**
- normalized VCF path
- annotation resource configuration

**Writes to `state`:**
- annotated VCF path
- annotated variant table path
- annotation summary
- list of annotation resources used
- annotation completeness metrics

**Files created on disk:**
- annotated VCF
- annotated variant table

---

### Stage 8 — Global Filtering and Partitioning

**Reads from `state`:**
- annotated variant table path
- AF threshold configuration

**Writes to `state`:**
- filtered variant count summary
- coding-track table path
- non-coding-track table path
- coding/non-coding partition counts

**Files created on disk:**
- coding-track table
- non-coding-track table

---

### Stage 9 — Interpretation (Coding Track)

**Reads from `state`:**
- coding-track table path

**Writes to `state`:**
- interpreted coding-track table path
- coding-track prioritization summary
- coding-track warnings

**Files created on disk:**
- interpreted coding-track table

---

### Stage 10 — Interpretation (Non-Coding Track)

**Reads from `state`:**
- non-coding-track table path
- AlphaGenome availability flag (if optional step enabled)

**Writes to `state`:**
- interpreted non-coding-track table path
- non-coding-track prioritization summary
- AlphaGenome usage metadata (if used)
- non-coding-track warnings

**Files created on disk:**
- interpreted non-coding-track table
- optional AlphaGenome output files

---

### Stage 11 — Variant Prioritization

**Reads from `state`:**
- interpreted coding-track table path
- interpreted non-coding-track table path

**Writes to `state`:**
- prioritized variant table path
- prioritization summary
- top candidate list

**Files created on disk:**
- prioritized variant table

---

### Stage 12 — Validation

**Reads from `state`:**
- prioritized variant table path
- sorted BAM path
- BAM index path

**Writes to `state`:**
- validation candidate list
- IGV review targets
- validation notes path (if created)

**Files created on disk:**
- optional validation notes file

---

### Stage 13 — Report Generation

**Reads from `state`:**
- prioritized variant table path
- QC summaries
- annotation summaries
- prioritization summary
- validation summary

**Writes to `state`:**
- summary report path
- final run status
- end time

**Files created on disk:**
- summary report
- final metadata snapshot (optional)

---

### Error Handling Rule

If a stage cannot find a required input in `state`, it must:

1. record the failure in pipeline logs
2. append a clear error message to the error section of `state`
3. stop execution or fail the stage explicitly

---

### Implementation Note

This contract defines stage responsibilities, not internal code style.

SWE may implement the `state` object as:
- a nested dictionary
- a dataclass
- a pydantic model

As long as:
- required keys are explicit
- stage boundaries are preserved
- serialization and reproducibility are maintained

# End of SOP