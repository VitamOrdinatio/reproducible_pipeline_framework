# Architecture — reproducible_pipeline_framework

---

## 1. Repository Role

This repository provides a reusable framework for building **reproducible computational pipelines**, with emphasis on:

- configuration-driven execution  
- modular pipeline stages  
- structured logging  
- run metadata capture  
- standardized directory structure  
- traceable and reproducible outputs  

This is an **infrastructure repository**, not a domain-specific analysis project.

It defines the **engineering patterns** that downstream repositories will follow, including:

- rnaseq_pipeline  
- variant_annotation_pipeline  
- rare_disease_gene_prioritization  
- picu_harmonization  
- variant_database (partial adoption)  

This repository defines the baseline engineering standard for all downstream computational workflows in the portfolio.

---

## 2. Architectural Goal (Version 1)

Version 1 should demonstrate a **minimal, fully reproducible pipeline** that:

1. Executes via CLI using a configuration file  
2. Uses modular, function-based pipeline stages  
3. Creates a unique run directory for each execution  
4. Captures logs and metadata per run  
5. Preserves configuration used for execution  
6. Produces structured intermediate and final outputs  
7. Demonstrates SOP → code → output alignment  

The goal is **clarity and reproducibility**, not feature completeness.

---

## 3. Current Scaffold (Observed)

The current repository scaffold includes:

- `data/`
  - `raw/`
  - `interim/`
  - `processed/`
- `docs/`
- `environment/`
- `results/`
  - `tables/`
  - `figures/`
- `scripts/`
- `src/`
- `tests/`

This is a strong base but requires **specialization for pipeline framework behavior**.

---

## 4. Required Structural Additions

To support pipeline execution, the following must be added:

### New directories
- `config/`  
- `pipeline/`  
- `results/runs/`  

### New files
- `run_pipeline.py`  
- `requirements.txt`  
- optional: `Makefile`  

These additions introduce:
- configuration layer  
- execution layer  
- stage modularization  
- run-level reproducibility  

---

## 5. Final Repository Structure (Adjusted)
```
reproducible_pipeline_framework/
├── README.md
├── LICENSE
├── run_pipeline.py
├── requirements.txt
├── Makefile
│
├── config/
│   └── config.yaml
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── example/
│
├── docs/
│   ├── architecture.md
│   ├── conventions.md
│   ├── data_schema.md
│   ├── example_pipeline.md
│   ├── notes.md
│   ├── QC_template.md
│   ├── roadmap.md
│   ├── SOP_pipeline_example.md
│   ├── SOP_template.md
│   └── workflow.md
│
├── environment/
│   └── README.md
│
├── pipeline/
│   ├── stage_01_load_data.py
│   ├── stage_02_validate_data.py
│   ├── stage_03_clean_data.py
│   ├── stage_04_transform_data.py
│   ├── stage_05_analyze_data.py
│   └── stage_06_write_summary.py
│
├── results/
│   ├── runs/
│   ├── tables/
│   └── figures/
│
├── scripts/
│   ├── validation/
│   └── README.md
│
├── src/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── file_utils.py
│   ├── logger.py
│   ├── metadata.py
│   ├── path_manager.py
│   └── pipeline_runner.py
│
└── tests/
    ├── unit/
    ├── integration/
    ├── validation/
    └── README.md
```

---

## 6. Architectural Layers

This repository is organized into three logical layers:

### 6.1 Framework Layer (`src/`)

Responsible for:

- configuration loading  
- path resolution  
- logging  
- metadata tracking  
- pipeline orchestration  

### 6.2 Pipeline Layer (`pipeline/`)

Contains:

- stage modules  
- domain-specific logic  
- sequential execution steps  

Each stage should perform **one logically distinct transformation step** and be independently testable.

### 6.3 Documentation and SOP Layer (`docs/`)

Defines:

- architecture  
- SOP templates  
- workflow explanations  
- conventions and standards  

---

## 7. Execution Model

Pipeline execution:

```bash
python run_pipeline.py --config config/config.yaml
```

Execution flow:

1. Parse CLI arguments
2. Load config
3. Create run directory
4. Initialize logger
5. Save config snapshot
6. Execute pipeline stages
7. Write outputs
8. Generate metadata
9. Exit with success or failure

---

## 8. Run Directory Design

Each run produces an isolated output directory:

```text
results/runs/run_YYYY_MM_DD_HHMMSS/
├── logs/
│   └── pipeline.log
├── interim/
├── final/
├── reports/
├── metadata.json
└── config_used.yaml
```

Key principles:

- Never overwrite previous runs
- Each run is independently reproducible

`results/runs/` is the authoritative location for execution outputs, while `results/tables/` and `results/figures/` are reserved for curated summaries.

Each run directory is self-contained and sufficient to reproduce results independently.

---

## 9. Configuration System

Configuration is YAML-based:

`config/config.yaml`

Defines:

- input paths
- output locations
- pipeline parameters
- stage toggles
- logging settings

Pipeline behavior must be driven by configuration, not hard-coded values.

---

## 10. Function-Based Stage Design

Each stage module exposes a function:

```python
def run_stage(config, paths, logger, state):
    return updated_state
```

Inputs:

- config → runtime parameters
- paths → resolved directories
- logger → logging object
- state → shared data between stages

Output:

- updated state dictionary

This design ensures:

- simplicity
- testability
- transparency
- modular reuse

---

## 11. Pipeline Stages (Example)

| Stage     | Module                     |
| --------- | -------------------------- |
| Load data | stage_01_load_data.py      |
| Validate  | stage_02_validate_data.py  |
| Clean     | stage_03_clean_data.py     |
| Transform | stage_04_transform_data.py |
| Analyze   | stage_05_analyze_data.py   |
| Summarize | stage_06_write_summary.py  |


---

## 12. Data Flow

Standard flow:
`data/raw → data/interim → data/processed → results/runs/ → results/tables`

Raw data is never overwritten.

---

## 13. Logging Strategy

Logging is required for reproducibility.

Each run generates:

- pipeline log file
- stage execution logs
- error tracking

Location:
```text
results/runs/<run_id>/logs/pipeline.log
```

---

## 14. Metadata Strategy

Each run generates:

`metadata.json`

Includes:

- run ID
- timestamps
- config used
- pipeline version
- stage status
- success/failure

---

## 15. SOP Integration

The SOP system maps directly to the architecture:

| SOP Section     | Implementation           |
| --------------- | ------------------------ |
| Inputs          | config + data/raw        |
| Outputs         | data/processed + results |
| Procedure       | pipeline/stage_*.py      |
| Logging         | logs/                    |
| Reproducibility | config + metadata        |
| QC              | scripts/validation       |

SOP is not documentation only — it reflects execution.

---

## 16. Testing Strategy

Testing structure:

- unit → individual modules
- integration → full pipeline run
- validation → output correctness

Tests should verify:

- pipeline runs end-to-end
- outputs exist
- logs exist
- metadata exists

Tests should be runnable via a single command (e.g., `pytest`).

---

## 17. Design Constraints

Version 1 must intentionally avoid:

- workflow engines (Snakemake, Nextflow)
- DAG scheduling
- checkpoint restart systems
- container-first complexity
- HPC integration
- database-backed run tracking

These are deferred to future versions.

---

## 18. Risks and Cautions

Primary risks:

- overengineering too early
- mixing framework and pipeline logic
- duplicating logs across locations
- breaking separation of raw/interim/processed data
- allowing SOP to drift from implementation

---

## 19. Definition of Version 1 Success

Version 1 is complete when:

- pipeline runs from CLI
- config controls execution
- stages are modular
- run directories are created
- logs are generated
- metadata is captured
- outputs are structured
- SOP maps cleanly to implementation
- repository is understandable to external reviewers

---

## 20. Final Summary

This repository defines a minimal, reproducible pipeline architecture based on:

- configuration-driven execution
- modular functional stages
- structured run outputs
- logging and metadata
- SOP-aligned documentation

It serves as the engineering foundation for all future pipeline repositories in the portfolio.

---