# Reproducible Pipeline Framework

## Overview

This repository implements a modular, configuration-driven framework for building reproducible scientific data pipelines.

The purpose of this project is not to solve a single biological problem, but to define a **generalizable architecture** for:

- organizing computational workflows  
- enforcing reproducibility  
- separating configuration from execution  
- standardizing data flow across pipeline stages  

This framework is designed to support downstream projects in:

- variant annotation  
- RNA-seq analysis  
- rare disease gene prioritization  
- clinical data harmonization  

This repository includes a fully operational demonstration pipeline that can be executed end-to-end.

---

## Key Features

- Configuration-driven execution (YAML-based)
- Modular stage-based pipeline design
- Strict separation of code, data, and outputs
- Run-specific output directories
- Automatic logging and metadata tracking
- Reproducible execution with config snapshots
- Minimal dependency footprint

---

## Working Example Pipeline

This repository includes a fully operational six-stage demonstration pipeline.

Each stage operates on a shared state object, enabling explicit data flow between stages without reliance on global variables.

### Pipeline Stages

1. Load Data  
2. Validate Data  
3. Clean Data  
4. Transform / Annotate Data  
5. Analyze / Prioritize Variants  
6. Write Summary Outputs  

---

## Repository Structure

    reproducible_pipeline_framework/
    ├── config/
    │   └── config.yaml
    ├── data/
    │   ├── example/
    │   ├── interim/
    │   ├── processed/
    │   └── raw/
    ├── docs/
    ├── pipeline/
    ├── src/
    ├── results/
    │   └── runs/
    ├── run_pipeline.py
    ├── requirements.txt
    └── README.md

---

## Quick Start

From the repository root:

### Create virtual environment

    python3 -m venv .venv
    source .venv/bin/activate

### Install dependencies

    pip install -r requirements.txt

### Run pipeline

    python run_pipeline.py --config config/config.yaml

---

## Pipeline Execution Flow

VCF → Load → Validate → Clean → Annotate → Filter → Report

---

## Example Outputs

Each run generates:

    results/runs/run_YYYY_MM_DD_HHMMSS/

Including:

- logs/pipeline.log  
- metadata.json  
- config_used.yaml  
- final/prioritized_variants.tsv  
- reports/pipeline_summary.txt  

---

## Reproducibility Model

Each run directory contains all artifacts required to reproduce the analysis independently.

- configuration-driven  
- fully logged  
- self-contained  
- reproducible  

---

## Design Philosophy

- Explicit over implicit  
- Configuration over hardcoding  
- Modular over monolithic  
- Reproducible over ad hoc  

---

## Current Status

Version 1 comprises:

- a complete scaffold  
- a working six-stage pipeline  
- a reproducible execution state  

Version 1 is fully operational and supports end-to-end execution of the demonstration pipeline.

---

## Notes

- Placeholder annotation logic  
- Not for clinical use  

---

## License

See LICENSE file