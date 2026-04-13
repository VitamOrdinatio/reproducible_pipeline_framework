# Architecture  
## reproducible_pipeline_framework v2

---

## 1. Purpose

This document describes the software architecture of
`reproducible_pipeline_framework` Version 2.

It explains:

- project layout
- execution model
- state and data flow
- stage orchestration
- artifact management
- design principles

This architecture is designed to be modular, reproducible, and extensible,
and serves as the foundation for downstream pipeline repositories.

---

## 2. Design Goals

The architecture is built around the following principles:

- reproducibility
- modularity
- explicit data contracts
- transparent execution
- auditability
- extensibility

Key design goals:

- make data flow explicit
- avoid hidden state
- separate orchestration from stage logic
- allow incremental development
- support future pipeline repos

---

## 3. Repository Structure

```text
reproducible_pipeline_framework/
├── config/
│   └── config.yaml
│
├── data/
│   ├── example/
│   ├── interim/
│   ├── processed/
│   └── raw/
│
├── docs/
│   ├── SOP_pipeline_example.md
│   ├── state_contract_v2.md
│   ├── workflow.md
│   ├── architecture.md
│   └── ...
│
├── pipeline/
│   ├── stage_01_load_data.py
│   ├── stage_02_align_data.py
│   ├── ...
│   └── stage_13_write_summary.py
│
├── results/
│   ├── runs/
│   ├── tables/
│   └── figures/
│
├── src/
│   ├── config_loader.py
│   ├── path_manager.py
│   ├── pipeline_runner.py
│   ├── logger.py
│   ├── metadata.py
│   └── ...
│
├── tests/
├── run_pipeline.py
└── requirements.txt
```

---

## 4. Execution Entry Point

The pipeline is executed via:

```bash
python run_pipeline.py --config config/config.yaml
```

Execution flow:

1. configuration is loaded
2. paths are initialized
3. run metadata is created
4. state object is initialized
5. stages are executed sequentially
6. outputs and metadata are written

---

## 5. Orchestration Layer

The orchestration layer lives in:

- `src/pipeline_runner.py`

Responsibilities:

- determine execution mode
- manage stage execution order
- pass `state` between stages
- capture errors and warnings
- ensure run completion and metadata persistence

The orchestration layer does not perform analysis logic.

---

## 6. Stage Model

Each stage is implemented as:

- one Python module
- a single entry function:

```python
def run_stage(config, paths, logger, state) -> dict
```

Each stage:

- receives the shared state
- reads required inputs
- performs computation
- writes outputs to disk
- updates `state`

Stages do not directly call each other.

---

## 7. State and Data Flow

The `state` object is the single source of truth for pipeline execution.

It tracks:

- inputs
- artifacts
- QC metrics
- stage outputs
- warnings and errors
- run metadata

The state contract is defined in:

- `docs/state_contract_v2.md`

---

## 8. Data Persistence Strategy

Large data objects are never stored in memory inside `state`.

Instead:

- data are written to disk
- file paths are stored in `state`

Examples:

- BAM files
- VCF files
- TSV tables
- QC reports

This enables:

- reproducibility
- memory efficiency
- restart and inspection

---

## 9. Directory Strategy

Outputs are organized into run-specific directories:

```text
results/
  runs/
    <run_id>/
      final/
      validation/
      reports/
      logs/
      metadata.json
```

This ensures:

- run isolation
- auditability
- reproducibility

---

## 10. Execution Modes

### Full Pipeline Mode

Used when FASTQ input is provided.

Pipeline executes:

- alignment
- BAM processing
- QC
- variant calling
- downstream interpretation

---

### Annotation-Only Mode

Used when a VCF is provided.

Pipeline skips:

- alignment
- BAM processing
- variant calling

And begins at:

- VCF normalization

---

## 11. Automation vs Manual Boundaries

### Automated

- alignment
- BAM processing
- QC
- variant calling
- normalization
- annotation
- filtering
- interpretation
- prioritization
- validation preparation
- summary reporting

---

### Manual

- IGV-based review
- biological interpretation decisions

Manual review is explicitly outside the automated pipeline.

---

## 12. Error Handling

- errors are captured and logged
- failures are surfaced via `state["errors"]`
- pipeline halts on unrecoverable errors
- partial results remain available for inspection

---

## 13. Extensibility

This framework is designed to:

- support additional pipelines
- allow replacement of mock stages with real tools
- integrate richer QC and validation
- support clinical-grade workflows in downstream repos

---

## 14. Relationship to Downstream Pipelines

This repository provides:

- execution scaffolding
- state management
- stage orchestration patterns

Downstream pipelines (e.g. `variant_annotation_pipeline`) are expected to:

- reuse this architecture
- replace placeholder logic with real tools
- extend stages with domain-specific logic

---

## 15. Summary

This architecture emphasizes:

- explicit data flow
- modularity
- reproducibility
- transparency
- extensibility

It provides a foundation for robust, inspectable, and scalable bioinformatics pipelines.

---

# End of Architecture Document