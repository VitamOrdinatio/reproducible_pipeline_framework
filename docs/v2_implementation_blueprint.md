# V2 Implementation Blueprint  
## reproducible_pipeline_framework

---

## Purpose

This document defines the implementation plan for **Version 2** of `reproducible_pipeline_framework`.

Version 2 replaces the Version 1 six-stage toy variant-interpretation demo with a new **13-stage traditional genomics pipeline framework** based on the current `SOP_pipeline_example.md`.

The goal of v2 is to make the framework more realistic, more directly aligned with downstream genomics workflows, and easier to deploy into the future `variant_annotation_pipeline` repository.

This blueprint serves as the bridge between:

- SOP design  
- architectural refactor  
- scaffold evolution  
- executable implementation  

---

## V2 Design Principles

Version 2 should follow these principles:

- Replace v1 as the active implementation model
- Preserve v1 through Git history and release tagging rather than coexistence in the working tree
- Bind the SOP at the level of docs, scaffold, config, and code
- Remain runnable end-to-end on toy data
- Use lightweight or mocked implementations for external-tool-heavy stages where appropriate
- Use a clearer nested `state` contract
- Keep filenames and modules in lowercase snake_case
- Preserve the framework identity of the repository rather than turning it fully into the flagship real-data variant pipeline

---

## V2 Scope

Version 2 introduces a new traditional genomics pipeline model with the following characteristics:

- full-pipeline mode: FASTQ to prioritized report
- annotation-only mode: VCF to prioritized report
- path-centric state tracking
- expanded stage contracts
- dual-track variant interpretation:
  - coding track
  - non-coding track

Version 2 does **not** require immediate real-tool execution for every stage. Where necessary, stages may initially use mocked or simplified implementations that preserve:

- stage boundaries
- state contract behavior
- artifact creation
- config structure
- logging and metadata

This keeps the framework runnable while preparing the architecture for downstream real-tool deployment in `variant_annotation_pipeline`.

---

## Canonical V2 Stage Model

The active v2 pipeline should use the following stage sequence:

1. `stage_01_load_data.py`
2. `stage_02_align_data.py`
3. `stage_03_process_bam.py`
4. `stage_04_qc_aligned_reads.py`
5. `stage_05_call_variants.py`
6. `stage_06_normalize_vcf.py`
7. `stage_07_annotate_variants.py`
8. `stage_08_filter_and_partition.py`
9. `stage_09_interpret_coding.py`
10. `stage_10_interpret_noncoding.py`
11. `stage_11_prioritize_variants.py`
12. `stage_12_validate_variants.py`
13. `stage_13_write_summary.py`

These stage names should become the canonical active model for `pipeline/`.

---

## Execution Modes

Version 2 should support two execution modes:

### 1. `full_pipeline`
Input:
- FASTQ

Flow:
- FASTQ → alignment → BAM → VCF → annotation → interpretation → reporting

### 2. `annotation_only`
Input:
- VCF

Flow:
- VCF → normalization → annotation → interpretation → reporting

Execution mode should be defined explicitly in `config/config.yaml` and propagated into the shared `state` object.

---

## V2 State Contract

Version 2 replaces the looser v1 state model with a more explicit nested dictionary contract.

The state object should remain a plain Python dictionary for now, but it should be structured and consistent.

### Proposed Top-Level Keys

    state = {
        "run": {},
        "sample": {},
        "inputs": {},
        "artifacts": {},
        "qc": {},
        "annotations": {},
        "tracks": {},
        "reports": {},
        "stage_outputs": {},
        "warnings": [],
        "errors": [],
    }

### Key Design Rules

- Prefer file paths over large in-memory artifacts
- Each stage should read only what it requires
- Each stage should write only what it produces
- Missing required keys should fail clearly
- Large files should live on disk and be referenced by path
- The state object should support both execution modes

### Typical Contents

Examples of state fields may include:

- `state["run"]["run_id"]`
- `state["run"]["mode"]`
- `state["sample"]["sample_id"]`
- `state["inputs"]["fastq_1"]`
- `state["inputs"]["fastq_2"]`
- `state["inputs"]["input_vcf"]`
- `state["artifacts"]["aligned_bam"]`
- `state["artifacts"]["sorted_bam"]`
- `state["artifacts"]["bam_index"]`
- `state["artifacts"]["raw_vcf"]`
- `state["artifacts"]["normalized_vcf"]`
- `state["artifacts"]["annotated_table"]`
- `state["tracks"]["coding_table"]`
- `state["tracks"]["noncoding_table"]`
- `state["artifacts"]["prioritized_table"]`
- `state["reports"]["summary_report"]`
- `state["qc"]["alignment"]`
- `state["qc"]["variant_calling"]`
- `state["warnings"]`
- `state["errors"]`

---

## V2 Configuration Direction

`config/config.yaml` should be refactored to support the new stage model and execution modes.

### New Config Requirements

Version 2 config should include sections for:

- project metadata
- execution mode
- input paths
- reference resources
- external tools
- stage toggles
- filtering thresholds
- interpretation options
- output paths
- metadata settings

### Representative Config Sections

Examples of likely config sections:

- `project`
- `run`
- `mode`
- `paths`
- `references`
- `tools`
- `logging`
- `stages`
- `filtering`
- `annotation`
- `interpretation`
- `outputs`
- `metadata`

Version 2 config should be more expressive than v1, but still readable and manually editable.

---

## Repository Refactor Goals

Version 2 should refactor the repository so that the codebase, scaffold, and documentation all reflect the new canonical pipeline.

### Docs
Update:

- `docs/architecture.md`
- `docs/workflow.md`
- `docs/SOP_pipeline_example.md`
- `docs/example_pipeline.md`
- optionally `docs/roadmap.md`

### Pipeline
Replace the v1 six-stage pipeline files with the v2 13-stage files.

### Core Engine
Refactor:

- `src/pipeline_runner.py`
- `src/config_loader.py`
- `src/path_manager.py`
- `src/metadata.py` as needed

### Supporting Hygiene
Review:

- `.gitignore`
- `requirements.txt`
- `README.md`

---

## V2 Development Phases

## Phase 1 — Design Binding

### Objective
Bind the new SOP to architecture, workflow, and execution design before refactoring code.

### Tasks
- update `docs/architecture.md`
- update `docs/workflow.md`
- align `docs/SOP_pipeline_example.md` with the canonical v2 stage model
- define v2 execution modes
- define the nested `state` contract explicitly
- define the new config contract
- define the canonical 13-stage file map

### Deliverables
- updated architecture docs
- explicit state contract
- explicit stage map
- explicit config direction

### Exit Criteria
- docs reflect v2 rather than v1
- stage sequence is finalized
- state structure is agreed upon
- config expansion is agreed upon

---

## Phase 2 — Scaffold Refactor

### Objective
Replace the v1 scaffold assumptions with the v2 stage scaffold.

### Tasks
- remove or replace v1 stage files in `pipeline/`
- create the new 13-stage stage files
- update scaffold references in docs
- confirm directory structure still supports framework behavior
- clean tracked artifacts such as `__pycache__/`
- verify `.gitignore` is correct

### Deliverables
- refactored `pipeline/`
- clean working tree structure
- updated scaffold references in docs

### Exit Criteria
- the active stage file layout matches the v2 SOP
- repo hygiene is clean
- no v1/v2 ambiguity remains in active scaffold

---

## Phase 3 — Core Engine Refactor

### Objective
Refactor the framework engine so it can support the v2 SOP.

### Tasks
- update `src/pipeline_runner.py` to use the 13-stage model
- add execution mode branching
- update `src/config_loader.py` for new config schema
- update `src/path_manager.py` for new artifacts and reports
- update metadata handling as needed
- ensure logger assumptions still work cleanly

### Deliverables
- updated runner
- updated config loader
- updated path manager
- updated metadata behavior

### Exit Criteria
- the runner can orchestrate the v2 stages
- mode selection works
- stage order is correct
- metadata and logs remain coherent

---

## Phase 4 — Stage Implementation

### Objective
Implement all v2 stages in a runnable toy/demo form.

### Tasks
- implement each of the 13 stages
- use lightweight or mocked behavior where external tools are not yet wired
- create toy artifacts consistent with expected FASTQ/BAM/VCF progression
- preserve realistic stage contracts even where behavior is simplified
- ensure each stage updates the nested state contract correctly

### Deliverables
- runnable v2 stage implementations
- toy data and toy artifact generation as needed
- realistic stage outputs and state updates

### Exit Criteria
- each stage can run without breaking the pipeline
- state updates are consistent
- toy artifacts exist where expected
- pipeline remains runnable end-to-end

---

## Phase 5 — Stabilization and Testing

### Objective
Validate the full v2 pipeline and finalize repo polish.

### Tasks
- run full-pipeline mode end-to-end on toy data
- run annotation-only mode end-to-end on toy data
- inspect logs, metadata, reports, and artifacts
- finalize `requirements.txt`
- finalize `.gitignore`
- update `README.md`
- add or expand minimal tests

### Deliverables
- successful toy runs
- stable config and requirements
- updated README
- validated outputs

### Exit Criteria
- full-pipeline toy run succeeds
- annotation-only toy run succeeds
- outputs are coherent
- docs reflect actual behavior
- repo is stable enough to serve as the v2 framework baseline

---

## External Tool Strategy

Version 2 should acknowledge real external bioinformatics tools, but should not require full production-grade deployment of every tool inside the framework repo immediately.

### Recommended Initial Strategy
- model tool-aware stages explicitly
- use lightweight placeholder behavior where needed
- preserve artifact expectations and stage contracts
- keep the pipeline runnable

### Tools Referenced by the SOP
Examples include:

- BWA-MEM
- samtools
- GATK
- ANNOVAR
- IGV
- AlphaMissense
- SpliceAI
- optional AlphaGenome

### Rule
The framework should model these steps clearly, but the first true real-tool deployment can occur more fully in `variant_annotation_pipeline`.

---

## Relationship to Downstream Repository

A core purpose of v2 is to serve as a landing pad for `variant_annotation_pipeline` v1.

The stronger and cleaner the v2 binding is in this framework repo, the easier it will be to deploy the next repo with:

- shared stage architecture
- shared config expectations
- shared state contract
- shared execution philosophy
- shared documentation model

In this sense, v2 is not only a framework refactor; it is also a preparatory architecture exercise for the next flagship genomics repository.

---

## What V2 Should Not Do

Version 2 should avoid:

- mixing v1 and v2 stage models in the active codebase
- overengineering the state model with dataclasses or pydantic too early
- turning the framework repo into the full real-data flagship pipeline
- depending on large real datasets
- requiring complex infrastructure before toy runs are stable

---

## Success Criteria for V2

Version 2 is successful when:

- the active framework reflects the new SOP
- the pipeline supports both `full_pipeline` and `annotation_only` modes
- the nested state contract is clear and enforced
- the 13-stage model is runnable on toy data
- logs, metadata, and outputs remain reproducible
- the repo serves as a strong template for `variant_annotation_pipeline`

---

## Immediate Next Step

Before any coding begins, the first implementation task should be:

- finalize the v2 stage map
- finalize the nested state schema
- finalize the v2 config direction

Only after those are stable should code refactoring begin.

---

# End of Blueprint