# Framework Roadmap  
## reproducible_pipeline_framework v2

---

## Purpose

This document outlines the forward-looking roadmap for the
`reproducible_pipeline_framework` repository.

The goal is to guide future enhancements while ensuring the framework remains
driven by real pipeline needs rather than abstract engineering.

---

## Completed (v2)

The following capabilities are already implemented:

- Modular 13-stage pipeline architecture
- Shared state contract with explicit data flow
- Config-driven execution
- Full pipeline execution on toy data
- Annotation-only execution mode (implemented, further testing planned)
- Automated QC scaffolding
- Variant filtering, interpretation, and prioritization stages
- Validation preparation for manual IGV review
- Structured run directories with logs, metadata, and reports
- Example dataset and runnable end-to-end execution

---

## Near-Term Goals

These are concrete improvements that strengthen the current framework:

- Fully validate and document `annotation_only` execution mode
- Expand automated QC metrics where feasible
- Add minimal integration tests to validate stage chaining
- Improve validation reporting (warnings, thresholds, QC summaries)
- Harden error handling and messaging for user-facing failures

---

## Mid-Term Goals

Enhancements that support reuse across additional pipelines:

- Replace placeholder tool logic with optional real tool wrappers
- Support optional external tool integration (e.g., aligners, variant callers)
- Expand configuration schema for greater flexibility
- Add standardized validation hooks for additional pipeline types
- Improve test coverage across stage modules

---

## Long-Term Goals

Forward-looking capabilities that may be added as downstream repos mature:

- Workflow graph support (non-linear execution)
- Parallel or distributed execution
- Richer metadata capture and provenance tracking
- Integration with real variant annotation and RNA-seq pipelines
- Reusable stage library shared across multiple repositories
- Schema validation for configuration and state

---

## Guiding Philosophy

This framework should:

- evolve incrementally based on real pipeline needs
- avoid premature abstraction
- prioritize clarity and reproducibility
- remain lightweight and understandable

New features should be introduced only when justified by concrete use cases.

---

# End of Roadmap