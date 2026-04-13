"""
Stage 07: Annotate variants.

Version 2 responsibilities:
- read the normalized VCF artifact from Stage 06
- create annotated VCF and annotated TSV artifacts
- attach lightweight functional, clinical, population-frequency,
  and AI-style placeholder annotations
- update annotation metadata and stage_outputs in state

This stage does not perform real ANNOVAR/VEP/ClinVar/gnomAD integration
inside the framework repo. Instead, it creates lightweight annotated outputs
that preserve:
- stage boundaries
- artifact creation
- state transitions
- logging and reproducibility
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


GENE_SYMBOL_MAP = {
    ("chr1", 123456): "POLG",
    ("chr1", 123789): "TWNK",
    ("chr2", 987654): "POLRMT",
    ("chr2", 555000): "TFAM",
    ("chrX", 111111): "LIG3",
}

CONSEQUENCE_MAP = {
    "A>G": "missense",
    "C>T": "nonsense",
    "G>A": "intronic",
    "T>C": "splice_site",
    "G>T": "regulatory",
}

CLINVAR_MAP = {
    "missense": "uncertain_significance",
    "nonsense": "likely_pathogenic",
    "intronic": "uncertain_significance",
    "splice_site": "pathogenic",
    "regulatory": "uncertain_significance",
}

AF_MAP = {
    ("chr1", 123456): 0.0002,
    ("chr1", 123789): 0.00001,
    ("chr2", 987654): 0.02,
    ("chr2", 555000): 0.0005,
    ("chrX", 111111): 0.005,
}

ALPHAMISSENSE_MAP = {
    "missense": 0.82,
    "nonsense": None,
    "intronic": None,
    "splice_site": None,
    "regulatory": None,
}

SPLICEAI_MAP = {
    "missense": 0.01,
    "nonsense": 0.02,
    "intronic": 0.12,
    "splice_site": 0.94,
    "regulatory": 0.05,
}


def validate_normalized_vcf(state: dict[str, Any]) -> Path:
    """
    Validate the normalized VCF artifact from Stage 06.

    Parameters
    ----------
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    Path
        Normalized VCF path.

    Raises
    ------
    ValueError
        If required artifact path is missing.
    FileNotFoundError
        If the normalized VCF file does not exist.
    """
    normalized_vcf = state["artifacts"].get("normalized_vcf")
    if not normalized_vcf:
        raise ValueError("Stage 07 requires artifacts.normalized_vcf.")

    normalized_vcf_path = Path(normalized_vcf)
    if not normalized_vcf_path.exists():
        raise FileNotFoundError(f"Normalized VCF not found: {normalized_vcf_path}")

    return normalized_vcf_path


def build_variant_key(ref: str, alt: str) -> str:
    """
    Build a REF>ALT key for consequence assignment.

    Parameters
    ----------
    ref : str
        Reference allele.
    alt : str
        Alternate allele.

    Returns
    -------
    str
        Variant key such as A>G.
    """
    return f"{ref}>{alt}"


def classify_variant_type(consequence: str) -> str:
    """
    Assign coding/non-coding class from consequence label.

    Parameters
    ----------
    consequence : str
        Consequence label.

    Returns
    -------
    str
        Variant class: coding or non-coding.
    """
    coding_consequences = {"missense", "nonsense", "frameshift", "splice_site", "synonymous"}
    return "coding" if consequence in coding_consequences else "non-coding"


def parse_vcf_to_dataframe(normalized_vcf_path: Path) -> pd.DataFrame:
    """
    Parse normalized VCF into a pandas DataFrame.

    Parameters
    ----------
    normalized_vcf_path : Path
        Path to normalized VCF.

    Returns
    -------
    pd.DataFrame
        Parsed VCF records as a DataFrame.
    """
    records: list[dict[str, Any]] = []

    with normalized_vcf_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                continue

            stripped = line.strip()
            if not stripped:
                continue

            fields = stripped.split("\t")
            if len(fields) < 8:
                continue

            chromosome = fields[0]
            position = int(fields[1])
            variant_id = fields[2]
            ref = fields[3]
            alt = fields[4]
            qual = fields[5]
            filt = fields[6]
            info = fields[7]

            variant_key = build_variant_key(ref, alt)
            consequence = CONSEQUENCE_MAP.get(variant_key, "intergenic")
            gene_symbol = GENE_SYMBOL_MAP.get((chromosome, position), "UNKNOWN")
            clinvar = CLINVAR_MAP.get(consequence, "unclassified")
            af_gnomad = AF_MAP.get((chromosome, position), 0.0)
            alphamissense = ALPHAMISSENSE_MAP.get(consequence)
            spliceai = SPLICEAI_MAP.get(consequence, 0.0)
            variant_type = classify_variant_type(consequence)

            records.append({
                "chromosome": chromosome,
                "position": position,
                "variant_id": variant_id,
                "reference_allele": ref,
                "alternate_allele": alt,
                "quality": qual,
                "filter": filt,
                "info": info,
                "gene_symbol": gene_symbol,
                "consequence": consequence,
                "variant_type": variant_type,
                "clinvar_classification": clinvar,
                "af_gnomad": af_gnomad,
                "af_exac": af_gnomad,
                "af_1kgenomes": af_gnomad,
                "alphamissense_score": alphamissense,
                "spliceai_score": spliceai,
            })

    return pd.DataFrame(records)


def build_annotated_vcf_lines(df: pd.DataFrame, normalized_vcf_path: Path) -> list[str]:
    """
    Build annotated VCF lines from the annotated DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Annotated variant DataFrame.
    normalized_vcf_path : Path
        Source normalized VCF path.

    Returns
    -------
    list[str]
        Annotated VCF lines.
    """
    lines = [
        "##fileformat=VCFv4.2",
        "##source=annovar_placeholder",
        f"##source_normalized_vcf={normalized_vcf_path}",
        '##INFO=<ID=GENE,Number=1,Type=String,Description="Gene symbol">',
        '##INFO=<ID=CONS,Number=1,Type=String,Description="Variant consequence">',
        '##INFO=<ID=VT,Number=1,Type=String,Description="Variant class">',
        '##INFO=<ID=CLINVAR,Number=1,Type=String,Description="ClinVar classification">',
        '##INFO=<ID=AFGNOMAD,Number=1,Type=Float,Description="gnomAD allele frequency">',
        '##INFO=<ID=ALPHAMISSENSE,Number=1,Type=String,Description="AlphaMissense score">',
        '##INFO=<ID=SPLICEAI,Number=1,Type=Float,Description="SpliceAI score">',
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO",
    ]

    for _, row in df.iterrows():
        alphamissense = "." if pd.isna(row["alphamissense_score"]) else str(row["alphamissense_score"])
        info = (
            f"GENE={row['gene_symbol']};"
            f"CONS={row['consequence']};"
            f"VT={row['variant_type']};"
            f"CLINVAR={row['clinvar_classification']};"
            f"AFGNOMAD={row['af_gnomad']};"
            f"ALPHAMISSENSE={alphamissense};"
            f"SPLICEAI={row['spliceai_score']}"
        )
        lines.append(
            f"{row['chromosome']}\t{row['position']}\t{row['variant_id']}\t"
            f"{row['reference_allele']}\t{row['alternate_allele']}\t"
            f"{row['quality']}\t{row['filter']}\t{info}"
        )

    return lines


def write_annotated_outputs(
    annotated_df: pd.DataFrame,
    normalized_vcf_path: Path,
    annotated_vcf_path: Path,
    annotated_table_path: Path,
) -> None:
    """
    Write annotated VCF and annotated TSV outputs.

    Parameters
    ----------
    annotated_df : pd.DataFrame
        Annotated variant table.
    normalized_vcf_path : Path
        Source normalized VCF path.
    annotated_vcf_path : Path
        Destination annotated VCF path.
    annotated_table_path : Path
        Destination annotated TSV path.
    """
    annotated_lines = build_annotated_vcf_lines(annotated_df, normalized_vcf_path)

    with annotated_vcf_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(annotated_lines) + "\n")

    annotated_df.to_csv(annotated_table_path, sep="\t", index=False)


def build_annotation_summary(annotated_df: pd.DataFrame) -> dict[str, Any]:
    """
    Build compact annotation metadata summary.

    Parameters
    ----------
    annotated_df : pd.DataFrame
        Annotated variant table.

    Returns
    -------
    dict[str, Any]
        Annotation summary dictionary.
    """
    row_count = len(annotated_df)

    def completeness(column: str) -> float:
        if row_count == 0 or column not in annotated_df.columns:
            return 0.0
        return round(float(annotated_df[column].notna().mean()), 3)

    return {
        "resources_used": ["ANNOVAR_placeholder", "ClinVar_placeholder", "gnomAD_placeholder", "AlphaMissense_placeholder", "SpliceAI_placeholder"],
        "annotation_fields_present": list(annotated_df.columns),
        "annotation_completeness": {
            "gene_symbol": completeness("gene_symbol"),
            "clinvar_classification": completeness("clinvar_classification"),
            "af_gnomad": completeness("af_gnomad"),
            "alphamissense_score": completeness("alphamissense_score"),
            "spliceai_score": completeness("spliceai_score"),
        },
        "ai_annotations_used": ["AlphaMissense", "SpliceAI"],
    }


def run_stage(
    config: dict[str, Any],
    paths: dict[str, Path | str],
    logger,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute Stage 07: annotate variants.

    Parameters
    ----------
    config : dict[str, Any]
        Parsed pipeline configuration.
    paths : dict[str, Path | str]
        Resolved pipeline paths.
    logger : logging.Logger
        Configured pipeline logger.
    state : dict[str, Any]
        Shared nested pipeline state.

    Returns
    -------
    dict[str, Any]
        Updated state.
    """
    logger.info("Stage 07: annotating variants.")

    normalized_vcf_path = validate_normalized_vcf(state)
    annotated_vcf_path = Path(paths["annotated_vcf"])
    annotated_table_path = Path(paths["annotated_table"])

    if not config["annotation"]["create_mock_annotations"]:
        raise ValueError("Stage 07 currently requires annotation.create_mock_annotations=true.")

    annotated_df = parse_vcf_to_dataframe(normalized_vcf_path)
    write_annotated_outputs(
        annotated_df=annotated_df,
        normalized_vcf_path=normalized_vcf_path,
        annotated_vcf_path=annotated_vcf_path,
        annotated_table_path=annotated_table_path,
    )

    annotation_summary = build_annotation_summary(annotated_df)
    annotated_vcf_size = annotated_vcf_path.stat().st_size
    annotated_table_size = annotated_table_path.stat().st_size
    row_count = len(annotated_df)

    state["artifacts"]["annotated_vcf"] = str(annotated_vcf_path)
    state["artifacts"]["annotated_table"] = str(annotated_table_path)
    state["annotations"] = annotation_summary
    state["qc"]["annotation_qc"] = {
        "annotation_completed": True,
        "mock_annotation": True,
        "annotated_variant_count": row_count,
        "annotated_vcf_size_bytes": annotated_vcf_size,
        "annotated_table_size_bytes": annotated_table_size,
    }
    state["stage_outputs"]["stage_07_annotate_variants"] = {
        "status": "success",
        "normalized_vcf": str(normalized_vcf_path),
        "annotated_vcf": str(annotated_vcf_path),
        "annotated_table": str(annotated_table_path),
        "annotated_variant_count": row_count,
        "annotated_vcf_size_bytes": annotated_vcf_size,
        "annotated_table_size_bytes": annotated_table_size,
    }

    logger.info(f"Annotated VCF written to: {annotated_vcf_path}")
    logger.info(f"Annotated table written to: {annotated_table_path}")
    logger.info(f"Annotated variant count: {row_count}")

    return state


if __name__ == "__main__":
    import logging

    from pipeline.stage_01_load_data import run_stage as run_stage_01_load_data
    from pipeline.stage_02_align_data import run_stage as run_stage_02_align_data
    from pipeline.stage_03_process_bam import run_stage as run_stage_03_process_bam
    from pipeline.stage_04_qc_aligned_reads import run_stage as run_stage_04_qc_aligned_reads
    from pipeline.stage_05_call_variants import run_stage as run_stage_05_call_variants
    from pipeline.stage_06_normalize_vcf import run_stage as run_stage_06_normalize_vcf
    from src.config_loader import load_config, validate_config
    from src.path_manager import initialize_run_paths
    from src.pipeline_runner import initialize_state

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    test_logger = logging.getLogger("stage_07_test")

    test_config = load_config("config/config.yaml")
    validate_config(test_config)
    test_paths = initialize_run_paths(test_config)
    test_state = initialize_state(test_config, "config/config.yaml", test_paths)

    test_state = run_stage_01_load_data(test_config, test_paths, test_logger, test_state)
    if test_state["run"]["mode"] == "full_pipeline":
        test_state = run_stage_02_align_data(test_config, test_paths, test_logger, test_state)
        test_state = run_stage_03_process_bam(test_config, test_paths, test_logger, test_state)
        test_state = run_stage_04_qc_aligned_reads(test_config, test_paths, test_logger, test_state)
        test_state = run_stage_05_call_variants(test_config, test_paths, test_logger, test_state)
    test_state = run_stage_06_normalize_vcf(test_config, test_paths, test_logger, test_state)
    test_state = run_stage(test_config, test_paths, test_logger, test_state)

    print("Stage 07 completed successfully.")
    print(test_state["stage_outputs"]["stage_07_annotate_variants"])