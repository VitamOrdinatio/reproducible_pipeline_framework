"""
Stage 05 Call Variants

Temporary v2 scaffold placeholder.
This file exists to satisfy the v2 stage map and pipeline runner imports.

It should be replaced with a real implementation during Phase 4.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute stage_05_call_variants.

    This is a temporary placeholder implementation for v2 scaffold refactor.
    """

    logger.info("Running stage_05_call_variants (mock variant-calling step).")

    state["stage_outputs"]["stage_05_call_variants"] = {
        "status": "placeholder",
        "description": "mock variant-calling step",
    }

    state["warnings"].append(
        "stage_05_call_variants is currently using a placeholder implementation."
    )

    return state
