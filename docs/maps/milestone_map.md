# Milestone Map: reproducible_pipeline_framework (RPF)

## Purpose

Provide a generalizable, reproducible pipeline framework for genomic workflows that supports:
- modular pipeline stages 
- configuration-driven execution 
- logging and auditability 
- consistent directory structure 
- reproducible runs 

This is not a biology repo—it is infrastructure for all other repos.

---

## Terminology

- "pipeline framework": reusable execution structure shared across multiple domain-specific pipelines
- "stage": a discrete processing step with defined inputs, outputs, and logging boundaries
- "run_id": unique identifier for one pipeline execution instance
- "reproducible run": execution in which the same inputs and configuration yield the same outputs

---

## Position in the Overall System

RPF is the infrastructure layer underlying selected portfolio pipelines.

Examples:
RPF conventions → VAP
RPF conventions → RSP
RPF conventions → future structured ingestion / analysis workflows

RPF does not define biological logic.
It defines how pipelines are structured, executed, logged, and reproduced.

---

## Strategic Value

Signals:
- software engineering maturity 
- reproducibility practices 
- pipeline design (not just scripting) 
- ability to support multiple workflows (VAP, RSP, etc.) 
- awareness of auditability requirements 

RPF operationalizes the project-wide reproducibility and documentation standards used by downstream pipelines.

---

## Core Run Model (v1)

RPF manages execution using a run-centric model.

Fields / artifacts:
- run_id
- config_path
- input_paths
- output_root
- log_path
- stage_name
- stage_status
- stage_start_time
- stage_end_time
- environment_metadata
- source_pipeline

---

### Example Run Record (v1)

- run_id: run_2026_001
- config_path: config/config.yaml
- input_paths: data/raw/example_input.tsv
- output_root: results/runs/run_2026_001/
- log_path: logs/run_2026_001.log
- stage_name: transform
- stage_status: completed
- stage_start_time: 2026-04-20T09:00:00
- stage_end_time: 2026-04-20T09:00:12
- environment_metadata: Python 3.12, local venv
- source_pipeline: vap_v1

---

## Framework Contract

RPF must provide reusable conventions for:
- configuration loading
- run isolation
- stage execution
- logging
- validation hooks
- structured outputs

Pipelines built on RPF must be able to inherit these behaviors without redefining framework logic from scratch.

---

## Downstream Impact

RPF ensures that:
- VAP outputs are reproducible and auditable
- RSP outputs are consistent across datasets
- downstream systems (VDB, RDGP) receive stable, structured inputs

---

## Milestones

### M1 — Canonical Structure (Scaffold Exists)

Define and implement:
- directory structure: 
    - config/ 
    - data/ (raw/interim/processed) 
    - results/ 
    - logs/ 
    - src/ 
    - scripts/ 
    - docs/ 
- entry point: 
    - run_pipeline.py or equivalent 
- basic config file: 
    - config.yaml 

Goal:
A standardized project structure that can be reused


---

### M2 — Pipeline Execution Model (Stages Work)

Implement:
- pipeline stages (even if simple): 
    - load 
    - validate 
    - transform 
    - analyze 
    - output 
- stage orchestration: 
    - sequential execution 
    - clear stage boundaries 
- minimal example pipeline (toy data)
 
Goal:
Framework can execute a full pipeline end-to-end

---

### M3 — Configuration + Reproducibility Layer

Add:
- config-driven parameters: 
    - input paths 
    - output paths 
    - run settings 
- run isolation: 
    - unique run directories 
    - timestamped outputs 
- reproducible execution: 
    - same inputs → same outputs
 
Goal:
Pipeline behavior is controlled and repeatable

---

### M4 — Logging + Auditability

Implement:
  - centralized logging system 
  - log file per run 
  - stage-level logging 
  - error capture 

Track:
  - run ID 
  - config used 
  - execution time 
  - input/output paths 

Goal:
Pipeline is auditable, not just executable

---

### M5 — Data Integrity + Validation Hooks

Add:
  - input validation (file existence, format checks) 
  - basic schema checks for intermediate data 
  - failure modes: 
      - missing files 
      - malformed inputs 

Define:
  - assumptions 
  - limitations 

RPF must support deterministic validation:
- identical inputs and configs produce identical outputs
- stage outputs are verifiable independently

Goal:
Pipeline does not silently fail or produce invalid outputs

---

### M6 — Example Pipeline (Demonstration Layer)

Provide:
  - small example dataset 
  - complete example run 
  - expected outputs 

Document:
  - how to run 
  - what each stage does 
  - what outputs mean 

Goal:
External users can understand and reproduce behavior

---

### M7 — Documentation + Standards Alignment

Document:
  - objective of framework 
  - design philosophy 
  - assumptions 
  - limitations 
  - edge cases: 
      - large datasets 
      - partial failures 
      - reruns / overwrite behavior 
  - validation strategy: 
      - how correctness of pipeline stages would be tested 
  - implementation details: 
      - file formats 
      - expected environment 

Goal:
Repo is readable and credible to external reviewers


---

## Release Gate (Public v1.0)

RPF is portfolio-ready when:
  - pipeline runs end-to-end reproducibly 
  - config controls behavior 
  - logs capture execution details 
  - directory structure is consistent and reusable 
  - example pipeline is included and works 
  - documentation includes: 
      - assumptions 
      - limitations 
      - edge cases 
      - validation strategy 
      - implementation details

---

## Future Upgrades (Post v1.0)

- parallel execution support
- plugin-style stage modules
- integration with specific pipelines (VAP, RSP)
- more robust validation layers
- containerization (optional, later—not required early)
- performance tuning

---

## Graphical Summary

```text
RPF → defines execution conventions for:
    VAP
    RSP
    future structured pipeline repos

RPF provides:
    config-driven execution
    run isolation
    logging
    validation hooks
    reproducible outputs

Downstream domain repos define:
    what biological problem is being solved

RPF defines:
    how the pipeline is structured and executed
```

---

## One Sentence Summary
- RPF defines how pipelines behave;
- VAP and RSP define what pipelines do.