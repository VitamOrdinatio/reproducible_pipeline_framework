# Scripts Directory  
## reproducible_pipeline_framework v2

---

## Purpose

The `scripts/` directory is reserved for auxiliary, utility, or developer-facing scripts that support pipeline development, testing, or maintenance.

In Version 2 of this framework, the primary pipeline execution logic does **not** live here.

Instead, the pipeline is implemented as:

- modular stage files in `pipeline/`
- orchestrated via `run_pipeline.py`
- supported by reusable code in `src/`

---

## What Belongs Here

Examples of appropriate scripts for this directory:

- helper utilities for data preparation
- one-off developer tools
- dataset converters
- small analysis helpers
- benchmarking or profiling helpers
- manual data sanity checks

Scripts placed here should:

- not be required for the core pipeline to run
- not duplicate logic from `pipeline/` or `src/`

---

## What Does *Not* Belong Here

The following should **not** be placed in this directory:

- pipeline stage implementations
- core orchestration logic
- reusable libraries
- configuration or schema definitions

Those belong in:

- `pipeline/`
- `src/`
- `config/`
- `docs/`

---

## Current Status

This directory is intentionally empty in v2.

It exists to provide a clear location for future developer tools without cluttering the main pipeline code.

---

## Future Use Cases

Potential future contents:

- data preparation scripts
- synthetic dataset generators
- exploratory analysis helpers
- visualization helpers
- benchmarking scripts

---

# End of Scripts README