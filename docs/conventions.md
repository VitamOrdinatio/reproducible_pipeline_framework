# Pipeline Conventions

## Purpose

This document defines conventions for building reproducible scientific pipelines using this framework.

These conventions are intended to make projects:

- Easier to understand
- Easier to rerun
- Easier to debug
- Easier to extend
- Easier to share

---

## Directory Conventions

### docs/
Documentation describing the pipeline, architecture, data schema, and workflow decisions.

### data/
Contains input and intermediate data.

- raw/ — original input data, never modified
- interim/ — intermediate files produced during processing
- processed/ — final cleaned or transformed datasets used for analysis

### scripts/
Entry-point scripts that execute pipeline steps.

### src/
Reusable code modules, libraries, parsers, validators, utilities, and processing logic.

### results/
Final outputs for interpretation.

- tables/
- figures/

### tests/
Test scripts and validation checks for pipeline components.

### environment/
Environment setup instructions, requirements files, and configuration notes.

---

## Step Naming Conventions

Pipeline steps should be clearly named and ordered when appropriate.

Examples:

- step01_validate_input
- step02_parse_variants
- step03_annotate_variants
- step04_filter_variants
- step05_generate_summary_tables
- step06_generate_figures

This makes the pipeline easier to follow and rerun step-by-step.

---

## Logging

Each pipeline step should log:

- start time
- end time
- input file(s)
- output file(s)
- number of records processed
- warnings or errors

Logs should be stored in a dedicated log directory or alongside results.

---

## Reproducibility Principles

Pipelines should aim to make it possible for another researcher to:

1. Obtain the same input data
2. Run the same scripts
3. Produce the same outputs
4. Understand the transformations performed
5. Verify intermediate results

Avoid hidden steps, manual edits, and undocumented transformations.

---

## Configuration Philosophy

Pipelines should avoid hardcoding:

- file paths
- thresholds
- parameter values
- database locations

Instead, these should be stored in configuration files or clearly defined variables.

---

## Documentation Expectations

Each project should document:

- Purpose of the project
- Input data format
- Output data format
- Pipeline steps
- Assumptions
- Limitations
