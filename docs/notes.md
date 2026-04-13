# Notes  
## reproducible_pipeline_framework v2

---

## Purpose

This document captures implementation notes, design observations, and non-blocking follow-up items for the v2 pipeline framework.

It is intentionally lighter than:

- `architecture.md`
- `workflow.md`
- `roadmap.md`

Use this file for:

- short design reminders
- implementation observations
- deferred refinements
- housekeeping notes that do not yet justify a roadmap item

---

## Current Status

Version 2 now includes:

- a 13-stage pipeline
- full-pipeline mode execution on toy FASTQ data
- annotation, partitioning, interpretation, prioritization, validation prep, and summary reporting
- a shared nested state contract
- run-specific output directories and metadata tracking

---

## Important Clarifications

### IGV
IGV is treated as a **manual downstream review tool**.

The pipeline does **not** automate IGV.

Instead, Stage 12 prepares:

- validation notes
- IGV review candidate list

---

## Deferred / Future Refinements

These are not blockers for v2, but may be improved later:

- explicit end-to-end test for `annotation_only` mode
- richer automated QC metrics
- more formal schema validation for `state`
- tighter integration tests
- richer example datasets
- replacement of placeholder tool logic with real tool wrappers in downstream repos

---

## Portfolio Notes

This repository is intended to demonstrate:

- pipeline architecture
- reproducibility
- staged artifact management
- state-aware orchestration
- documentation discipline

It is a framework repository, not a production clinical pipeline.

---

# End of Notes