# Example Pipeline

This document describes a simple example pipeline using the reproducible pipeline framework.

## Example Problem

We want to:

1. Read an input table
2. Validate required columns
3. Filter rows based on criteria
4. Write a processed output table
5. Generate a summary report

---

## Pipeline Steps

### Step 1 — Validate Input
Check that the input file contains required columns.

Input:
- data/raw/input.tsv

Output:
- data/interim/validated_input.tsv

---

### Step 2 — Filter Data
Apply filtering rules to remove unwanted rows.

Input:
- data/interim/validated_input.tsv

Output:
- data/processed/filtered_data.tsv

---

### Step 3 — Generate Summary
Produce a summary table describing the processed data.

Input:
- data/processed/filtered_data.tsv

Output:
- results/tables/summary.tsv

---

## Example Pipeline Flow
data/raw/input.tsv
↓
validate_input
↓
data/interim/validated_input.tsv
↓
filter_data
↓
data/processed/filtered_data.tsv
↓
generate_summary
↓
results/tables/summary.tsv


---

## Key Ideas Demonstrated

This toy pipeline demonstrates:

- Stepwise processing
- Separation of raw, interim, and processed data
- Clear input/output relationships
- Reproducible execution order
- Organized results
