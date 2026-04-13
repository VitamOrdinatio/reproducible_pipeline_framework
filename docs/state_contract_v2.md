# State Contract v2  
## reproducible_pipeline_framework

---

## 1. Purpose

The state contract defines the structure, expectations, and lifecycle of the
shared `state` object passed between pipeline stages in
`reproducible_pipeline_framework` v2.

The purpose of this contract is to:

- provide explicit data flow between stages
- enforce stage boundaries
- enable reproducibility
- support restart, audit, and debugging
- support both `full_pipeline` and `annotation_only` modes

This contract reflects the **actual implemented behavior** of the v2 pipeline.

---

## 2. Core Design Principles

1. The `state` object is a single, shared, mutable dictionary passed to every stage.
2. Each stage:
   - reads only the keys it requires
   - writes only the keys it owns
3. No stage should silently modify unrelated keys.
4. Large data objects are written to disk and referenced by path.
5. The state object is JSON-serializable.
6. All run-critical artifacts must be traceable through `state`.

---

## 3. Top-Level State Structure

```python
state = {
    "run": {},
    "sample": {},
    "inputs": {},
    "artifacts": {},
    "annotations": {},
    "qc": {},
    "stage_outputs": {},
    "warnings": [],
    "errors": [],
    "reports": {},
}
```

Each section is described below.

---

## 4. Run Metadata

```python
state["run"] = {
    "run_id": str,
    "mode": "full_pipeline" | "annotation_only",
    "config_path": str,
    "config_snapshot": str,
    "status": "initialized" | "success" | "failed",
}
```

**Owner:** initialized by pipeline runner  
**Updated by:** pipeline runner only

---

## 5. Sample Metadata

```python
state["sample"] = {
    "sample_id": str,
    "reference_genome": str,
}
```

**Owner:** Stage 01  
**Updated by:** Stage 01 only

---

## 6. Input Records

```python
state["inputs"] = {
    "fastq_1": str | None,
    "fastq_2": str | None,
    "input_vcf": str | None,
}
```

**Owner:** Stage 01  
**Purpose:** record raw user-provided inputs

---

## 7. Artifacts (Primary Outputs)

```python
state["artifacts"] = {
    "aligned_bam": str,
    "sorted_bam": str,
    "bam_index": str,
    "raw_vcf": str,
    "normalized_vcf": str,
    "annotated_vcf": str,
    "annotated_table": str,
    "filtered_table": str,
    "coding_table": str,
    "noncoding_table": str,
    "interpreted_coding_table": str,
    "interpreted_noncoding_table": str,
    "prioritized_table": str,
    "validation_notes": str,
    "summary_report": str,
}
```

**Owner:** individual stages  
**Purpose:** authoritative reference to files produced by the pipeline

---

## 8. Annotation Summary

```python
state["annotations"] = {
    "resources_used": list[str],
    "annotation_completed": bool,
}
```

**Owner:** Stage 07  
**Purpose:** record annotation provenance

---

## 9. Quality Control Records

```python
state["qc"] = {
    "input_qc": {},
    "alignment_qc": {},
    "bam_processing_qc": {},
    "variant_calling_qc": {},
    "annotation_qc": {},
    "validation_qc": {},
}
```

Each sub-dictionary is owned by a specific stage.

### Examples

```python
state["qc"]["alignment_qc"] = {
    "alignment_completed": True,
    "read_count": int,
}

state["qc"]["validation_qc"] = {
    "validation_completed": True,
    "manual_igv_review_required": True,
    "candidate_count": int,
}
```

---

## 10. Stage Output Summaries

```python
state["stage_outputs"] = {
    "stage_01_load_data": {...},
    "stage_02_align_data": {...},
    "stage_03_process_bam": {...},
    ...
    "stage_13_write_summary": {...},
}
```

**Purpose:**
- track per-stage metrics
- capture counts, file paths, and QC signals
- support downstream reporting

Each stage writes exactly one entry keyed by its stage name.

---

## 11. Warnings and Errors

```python
state["warnings"] = [str, ...]
state["errors"] = [str, ...]
```

**Purpose:**
- capture non-fatal warnings
- capture fatal errors
- surfaced in final summary report

---

## 12. Reports

```python
state["reports"] = {
    "summary_report": str,
    "summary_table": str,
    "report_line_count": int,
}
```

**Owner:** Stage 13  
**Purpose:** terminal reporting artifacts

---

## 13. Stage Read/Write Contract

Each stage must explicitly define:

- required input keys from `state`
- output keys written to `state`
- file artifacts created on disk
- QC signals generated
- warnings or errors appended

Example (Stage 11):

**Reads:**
- `artifacts["interpreted_coding_table"]`
- `artifacts["interpreted_noncoding_table"]`

**Writes:**
- `artifacts["prioritized_table"]`
- `stage_outputs["stage_11_prioritize_variants"]`

---

## 14. Execution Modes

### Full Pipeline Mode

Uses:
- FASTQ inputs
- alignment
- variant calling
- full workflow

### Annotation-Only Mode

Uses:
- VCF input
- normalization
- annotation
- interpretation
- prioritization

Stages adapt based on `state["run"]["mode"]`.

---

## 15. Serialization and Reproducibility

- `state` is JSON-serializable
- `metadata.json` records the state snapshot
- configuration snapshot stored per run
- run directories are self-contained

---

## 16. Design Guarantees

- deterministic execution for toy data
- explicit artifact boundaries
- no hidden dependencies
- reproducible results
- clean separation between automation and manual review

---

## 17. Future Extensions

- formal schema validation
- pydantic or dataclass-based enforcement
- richer QC metrics
- checkpointing and restart support

---

# End of State Contract v2