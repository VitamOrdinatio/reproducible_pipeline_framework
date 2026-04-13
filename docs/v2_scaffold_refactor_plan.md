# V2 Scaffold Refactor Plan  
## reproducible_pipeline_framework

---

## Purpose

This document defines the concrete Version 2 stage file map and scaffold refactor plan for `reproducible_pipeline_framework`.

The goal is to replace the active Version 1 six-stage demo scaffold with the new Version 2 thirteen-stage traditional genomics pipeline scaffold defined by:

- `docs/SOP_pipeline_example.md`
- `docs/v2_implementation_blueprint.md`
- `docs/state_contract_v2.md`

This document is intentionally operational. It is the bridge between architecture and implementation.

---

## V2 Refactor Goals

The scaffold refactor should achieve the following:

1. Remove ambiguity between v1 and v2 in the active codebase
2. Establish the canonical v2 stage file set
3. Align the `pipeline/` directory with the new SOP
4. Prepare the repo for execution modes:
   - `full_pipeline`
   - `annotation_only`
5. Preserve framework identity while improving realism
6. Keep the repo runnable on toy data
7. Keep external-tool-heavy steps mockable or lightweight in the framework repo

---

## Canonical V2 Stage File Map

The active `pipeline/` directory should use the following files:

    pipeline/
    ├── stage_01_load_data.py
    ├── stage_02_align_data.py
    ├── stage_03_process_bam.py
    ├── stage_04_qc_aligned_reads.py
    ├── stage_05_call_variants.py
    ├── stage_06_normalize_vcf.py
    ├── stage_07_annotate_variants.py
    ├── stage_08_filter_and_partition.py
    ├── stage_09_interpret_coding.py
    ├── stage_10_interpret_noncoding.py
    ├── stage_11_prioritize_variants.py
    ├── stage_12_validate_variants.py
    └── stage_13_write_summary.py

These filenames are the canonical active v2 implementation target.

All files should remain lowercase snake_case.

---

## Mapping from V1 Stage Files to V2 Stage Files

The current v1 stage set is:

- `stage_01_load_data.py`
- `stage_02_validate_data.py`
- `stage_03_clean_data.py`
- `stage_04_transform_data.py`
- `stage_05_analyze_data.py`
- `stage_06_write_summary.py`

### Direct Carryover

#### `stage_01_load_data.py`
- keep filename
- refactor behavior
- v2 must support:
  - FASTQ input for `full_pipeline`
  - VCF input for `annotation_only`
- must write into the new nested state structure

#### `stage_06_write_summary.py`
- replace with `stage_13_write_summary.py`
- logic may be partially reusable
- must be rewritten to use the new stage sequence and nested state structure

---

### V1 Files to Remove or Replace

#### Remove / replace:
- `stage_02_validate_data.py`
- `stage_03_clean_data.py`
- `stage_04_transform_data.py`
- `stage_05_analyze_data.py`

These represent the v1 six-stage demo model and should no longer remain as active canonical stages once the v2 scaffold is adopted.

---

## V2 Stage Origins and Intent

### Stage 01 — `stage_01_load_data.py`
Purpose:
- detect mode
- validate input paths
- initialize sample/run/input state

Mode support:
- `full_pipeline`
- `annotation_only`

Output type:
- input context only
- no heavy artifact required

---

### Stage 02 — `stage_02_align_data.py`
Purpose:
- represent alignment step
- in framework v2, initially allow mocked/lightweight BAM creation

Primary artifact:
- aligned BAM path

---

### Stage 03 — `stage_03_process_bam.py`
Purpose:
- represent BAM sorting and indexing

Primary artifacts:
- sorted BAM
- BAM index

---

### Stage 04 — `stage_04_qc_aligned_reads.py`
Purpose:
- represent QC on aligned reads

Primary outputs:
- alignment QC summary
- optional QC report artifact(s)

---

### Stage 05 — `stage_05_call_variants.py`
Purpose:
- represent variant calling

Primary artifact:
- raw VCF

---

### Stage 06 — `stage_06_normalize_vcf.py`
Purpose:
- normalize or clean VCF
- unify entry point for both modes

Primary artifact:
- normalized VCF

---

### Stage 07 — `stage_07_annotate_variants.py`
Purpose:
- annotate variants
- produce annotated VCF and/or annotated table

Primary artifacts:
- annotated VCF
- annotated table

---

### Stage 08 — `stage_08_filter_and_partition.py`
Purpose:
- apply AF and other global filters
- separate variants into:
  - coding track
  - non-coding track

Primary artifacts:
- coding-track table
- noncoding-track table

---

### Stage 09 — `stage_09_interpret_coding.py`
Purpose:
- interpret coding variants
- prioritize based on coding evidence

Primary artifact:
- interpreted coding table

---

### Stage 10 — `stage_10_interpret_noncoding.py`
Purpose:
- interpret non-coding variants
- optionally incorporate AlphaGenome-style logic later

Primary artifact:
- interpreted noncoding table

---

### Stage 11 — `stage_11_prioritize_variants.py`
Purpose:
- combine track outputs
- generate final prioritized table

Primary artifact:
- prioritized variant table

---

### Stage 12 — `stage_12_validate_variants.py`
Purpose:
- represent read-level or artifact-level validation

Primary artifacts:
- validation notes or validation target list

---

### Stage 13 — `stage_13_write_summary.py`
Purpose:
- generate final report outputs
- finalize run summaries

Primary artifacts:
- summary report
- summary tables

---

## Core Engine Files Requiring Refactor

The following framework files must be updated to support the v2 scaffold.

### 1. `src/pipeline_runner.py`
Must be refactored to:

- use the 13-stage registry
- support execution mode branching
- initialize the nested state structure
- preserve fail-fast behavior
- support stage skipping where appropriate

### 2. `src/config_loader.py`
Must be refactored to:

- validate the expanded v2 config schema
- recognize execution mode
- validate mode-specific required inputs
- support references/tools sections if introduced

### 3. `src/path_manager.py`
Must be refactored to:

- support additional artifact paths
- support v2 report and validation artifact expectations
- preserve the run-specific output model

### 4. `src/metadata.py`
Must be reviewed and likely expanded to:

- record execution mode
- record stage status across 13 stages
- record key artifact paths and resource use as needed

### 5. `run_pipeline.py`
May remain small, but should be reviewed to ensure:
- it still works with the new runner assumptions
- it reports mode and run summary cleanly

---

## Config Refactor Requirements

`config/config.yaml` must be expanded to support the v2 scaffold.

### Required new concepts

- execution mode
- FASTQ input paths
- optional input VCF
- reference resource paths
- tool declarations or mock-tool flags
- stage toggles for 13 stages
- filtering thresholds
- interpretation options
- validation options

### Expected config direction

Likely sections include:

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
- `validation`
- `outputs`
- `metadata`

---

## Data and Toy Artifact Strategy

The framework repo should remain runnable on toy data.

### Recommended v2 toy artifacts

Under `data/example/`, likely future files include:

- toy FASTQ pair
- toy input VCF
- optional toy reference placeholders
- small annotation helper files as needed

### Important rule

The framework repo should **not** become dependent on large real datasets.

Toy artifacts should be:
- small
- readable
- quick to run
- sufficient to test state transitions and file creation

---

## Scaffold Refactor Phases

## Phase 2A — Pipeline File Transition

Tasks:
- remove v1 stage files from active use
- add the 13 canonical v2 stage files
- preserve lowercase snake_case naming
- keep files importable and syntactically clean

Exit criteria:
- `pipeline/` matches the v2 stage list exactly

---

## Phase 2B — Core Engine Alignment

Tasks:
- update runner, config loader, and path manager to recognize v2
- initialize the nested v2 state shape
- support mode-aware branching

Exit criteria:
- framework internals recognize v2 stage names and state structure

---

## Phase 2C — Documentation Alignment

Tasks:
- update references in:
  - `architecture.md`
  - `workflow.md`
  - `example_pipeline.md`
  - `README.md` if needed
- ensure no active doc still describes the v1 six-stage scaffold as canonical

Exit criteria:
- docs and scaffold agree

---

## Phase 2D — Hygiene and Cleanup

Tasks:
- remove tracked `__pycache__/`
- verify `.gitignore`
- review stale outputs and references
- ensure no accidental v1 artifacts remain in active scaffold assumptions

Exit criteria:
- repo tree is clean and coherent

---

## Recommended File-Level Refactor Order

The v2 scaffold should be implemented in this order:

1. `docs/v2_scaffold_refactor_plan.md`
2. `docs/state_contract_v2.md`  
3. `config/config.yaml` redesign  
4. `src/config_loader.py` refactor  
5. `src/path_manager.py` refactor  
6. `src/pipeline_runner.py` refactor  
7. create/replace stage files in `pipeline/`  
8. update docs references  
9. run toy mode tests  

This order minimizes rework.

---

## What Should Be Deleted vs Kept

## Keep
- `docs/architecture.md`
- `docs/workflow.md`
- `docs/SOP_template.md`
- `docs/SOP_pipeline_example.md`
- `docs/v2_implementation_blueprint.md`
- `docs/state_contract_v2.md`
- `config/config.yaml`
- `src/`
- `run_pipeline.py`
- `README.md`

## Delete from tracked active scaffold assumptions
- v1 stage files once replaced
- tracked `__pycache__/`
- any stale file references that imply the six-stage demo is still the active canonical model

---

## Success Criteria

The scaffold refactor is successful when:

- the active `pipeline/` directory matches the 13-stage v2 model
- core engine files reference the new stage model
- execution modes are recognized
- the nested state contract becomes the active implementation target
- docs and scaffold no longer describe the v1 six-stage model as canonical
- the repo is ready for staged v2 implementation on toy data

---

## Immediate Next Implementation Step

After this plan is committed, the next concrete engineering task should be:

- redesign `config/config.yaml` for v2

That is the correct first code-adjacent step because:

- config defines execution mode
- config defines tool/resource expectations
- config drives the runner and state initialization
- config must stabilize before the new stage implementations can be wired correctly

---

# End of Refactor Plan