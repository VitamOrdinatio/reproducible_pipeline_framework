# Environment Setup  
## reproducible_pipeline_framework v2

---

## Purpose

This document describes how to set up the execution environment required to run
the `reproducible_pipeline_framework` pipeline.

This repository is designed to be:

- lightweight
- portable
- easy to run locally
- adaptable for downstream projects

---

## 1. System Requirements

Recommended:

- Linux (or WSL on Windows)
- Python 3.9+
- Standard UNIX shell environment

This repository is tested on:

- Linux environments
- WSL-based development environments

---

## 2. Python Environment

It is strongly recommended to use a Python virtual environment.

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the environment

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

This repository intentionally keeps dependencies minimal to:

- avoid environment conflicts
- support portability
- serve as a framework for downstream pipelines

---

## 4. Running the Pipeline

Once the environment is active and dependencies are installed:

```bash
python run_pipeline.py --config config/config.yaml
```

---

## 5. Notes on Reproducibility

- This repository avoids strict version pinning.
- Downstream repositories should define stricter environment constraints if needed.
- Users requiring fully reproducible environments may choose to:

  - pin package versions
  - use containerization
  - adopt environment managers (e.g., conda, mamba)

---

## 6. External Tools

The framework models tools such as:

- aligners
- variant callers
- annotation tools
- visualization tools (e.g., IGV)

However, this repository does **not** require external bioinformatics tools to run the example pipeline.

Downstream repositories are expected to integrate real tools.

---

## 7. Troubleshooting

If the pipeline fails:

- ensure the virtual environment is active
- verify dependencies are installed
- check `results/runs/<run_id>/logs/pipeline.log`
- confirm input files exist

---

# End of Environment Setup