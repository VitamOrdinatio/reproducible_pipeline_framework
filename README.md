# reproducible_pipeline_framework

A modular, reproducible pipeline framework for genomics data analysis.

This repository implements a 13-stage example workflow demonstrating how to structure a reproducible bioinformatics pipeline with:

- explicit state tracking
- modular stage execution
- clear artifact management
- deterministic outputs for toy data
- traceable execution metadata

This framework is intended as a template and scaffold for building real pipelines such as `variant_annotation_pipeline`.

---

## What This Repository Is

- A runnable example pipeline
- A scaffold for real analysis workflows
- A demonstration of reproducible pipeline architecture

## What This Repository Is Not

- Not a clinical pipeline
- Not production-grade variant interpretation
- Not a replacement for real variant annotation tools

---

## Example Data Included

This repository includes small toy datasets so the pipeline can be run end-to-end:

```
data/example/example_R1.fastq
data/example/example_R2.fastq
data/example/example_variants.vcf
```

These files enable:

- full pipeline execution (FASTQ-based)
- annotation-only execution (VCF-based)

---

## Pipeline Overview

The pipeline supports two execution modes:

### Full Pipeline Mode

```
FASTQ → Alignment → BAM Processing → QC → Variant Calling
     → VCF Normalization → Annotation → Filtering/Partitioning
     → Interpretation → Prioritization → Validation Prep → Summary
```

### Annotation-Only Mode

```
VCF → Normalization → Annotation → Filtering/Partitioning
    → Interpretation → Prioritization → Validation Prep → Summary
```

Execution mode is controlled via:

```
config/config.yaml
```

---

## Pipeline Stages

| Stage | Description |
|------|-------------|
| 01 | Load Data |
| 02 | Align Reads |
| 03 | Process BAM |
| 04 | QC Aligned Reads |
| 05 | Call Variants |
| 06 | Normalize VCF |
| 07 | Annotate Variants |
| 08 | Filter & Partition |
| 09 | Interpret Coding Variants |
| 10 | Interpret Non-coding Variants |
| 11 | Prioritize Variants |
| 12 | Prepare for IGV Review |
| 13 | Write Summary Reports |

---

## IGV and Validation

This pipeline does **not** automate IGV.

Instead:

- Stage 12 performs automated validation checks
- A review candidate list is generated
- Optional manual inspection is expected to occur outside the pipeline

---

## Running the Pipeline

### Requirements

- Python 3.9+
- Linux or WSL environment recommended
- Dependencies listed in `requirements.txt`

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
python run_pipeline.py --config config/config.yaml
```

To switch execution mode, edit:

```
config/config.yaml
```

---

## Outputs

Each run produces a self-contained run directory:

```
results/runs/<run_id>/
├── final/
├── validation/
├── reports/
├── logs/
└── metadata.json
```

---

## State Tracking

All pipeline stages read from and write to a shared `state` object.

The state object tracks:

- inputs
- outputs
- QC metrics
- artifacts
- warnings
- errors
- run metadata

The formal state contract is documented in:

```
docs/state_contract_v2.md
```

---

## Architecture

Key components:

- `run_pipeline.py` — entry point
- `src/pipeline_runner.py` — orchestration
- `pipeline/` — individual stages
- `src/path_manager.py` — path resolution
- `src/logger.py` — structured logging
- `docs/` — documentation and SOP

Full architecture is documented in:

```
docs/architecture.md
```

---

## Intended Use

This repository is designed to:

- demonstrate reproducible pipeline design
- provide a foundation for downstream repositories
- serve as a portfolio-grade example of pipeline engineering

This is a **framework repository**, not an analysis pipeline or clinical tool.

---

## Future Extensions

- integration of real bioinformatics tools
- cohort-level analysis
- structural variant support
- richer QC and validation layers
- formal schema validation

---

## License

See `LICENSE`.

---

# End of README