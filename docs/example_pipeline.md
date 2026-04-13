# Example Pipeline  
## reproducible_pipeline_framework v2

This document demonstrates a minimal end-to-end example run of the v2 pipeline using the provided toy dataset.

The goal is to illustrate:

- how to run the pipeline
- what files are consumed and produced
- how stage outputs flow through the system
- how artifacts and results are organized

This example uses the built-in toy FASTQ files.

---

## 1. Inputs

The example run uses the following input files:

```
data/example/example_R1.fastq
data/example/example_R2.fastq
```

These represent paired-end sequencing reads for a toy sample.

The pipeline is executed in `full_pipeline` mode.

---

## 2. Running the Pipeline

Activate the environment:

```bash
source .venv/bin/activate
```

Run the pipeline:

```bash
python run_pipeline.py --config config/config.yaml
```

---

## 3. Execution Flow

The following stages are executed:

1. Load Data
2. Align Reads
3. Process BAM
4. QC Aligned Reads
5. Call Variants
6. Normalize VCF
7. Annotate Variants
8. Filter and Partition
9. Interpret Coding Variants
10. Interpret Non-Coding Variants
11. Prioritize Variants
12. Prepare for IGV Review
13. Write Summary Reports

---

## 4. Key Artifacts Produced

### Interim Outputs

```
data/interim/aligned.bam
data/interim/aligned.sorted.bam
data/interim/aligned.sorted.bam.bai
data/interim/raw_variants.vcf
data/interim/normalized_variants.vcf
```

### Processed Outputs

```
data/processed/annotated_variants.vcf
data/processed/annotated_variants.tsv
```

### Final Results

```
results/runs/<run_id>/final/
results/runs/<run_id>/validation/
results/runs/<run_id>/reports/
results/runs/<run_id>/logs/
```

---

## 5. Manual Review (Optional)

Stage 12 prepares a candidate list for optional manual IGV review.

IGV is not run automatically.

---

## 6. Summary

This example demonstrates:

- staged execution
- explicit artifact creation
- reproducible state tracking
- separation of automation and manual review
- end-to-end run using toy data

This is a demonstration pipeline intended as a scaffold for downstream, domain-specific pipelines.