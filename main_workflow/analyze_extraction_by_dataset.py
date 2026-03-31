"""
Analyze extraction results per dataset.
Groups studies by dataset_used_standardized and reports counts and percentages
for study_type, task_type, outcomes_modeled, model_class, validation_level,
modalities, longitudinal_tier, and neuro-oncology domain fields.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "studies_with_extracted_data.jsonl"
OUTPUT_FILE = BASE_DIR / "reports" / "analysis_by_dataset.txt"

# Exclude "other" from per-dataset breakdown (studies using only non-listed datasets)
DATASET_EXCLUDE = {"other"}


def get_validation_level(extracted_data):
    """Return validation_level string; supports legacy validation_strategy."""
    ed = extracted_data or {}
    level = ed.get("validation_level")
    if isinstance(level, str) and level:
        return level
    vs = ed.get("validation_strategy") or {}
    internal = vs.get("internal_validation") == "yes"
    external = vs.get("external_validation") == "yes"
    prospective = vs.get("prospective_or_temporal_validation") == "yes"
    any_unclear = any(
        vs.get(k) in ("unclear", "unsure")
        for k in ("internal_validation", "external_validation", "prospective_or_temporal_validation")
    )
    if internal and external and prospective:
        return "internal_and_external_and_prospective"
    if internal and external:
        return "internal_and_external"
    if internal and prospective:
        return "internal_and_prospective"
    if internal:
        return "internal_only"
    if any_unclear:
        return "unclear"
    return "none"


def get_nested(ed, path):
    obj = ed
    for key in path:
        obj = (obj or {}).get(key)
    return obj


def count_field(path, studies, allow_list=False):
    """Count values of a field (single value or list of primitives) across studies."""
    c = Counter()
    for s in studies:
        ed = s.get("extracted_data") or {}
        obj = get_nested(ed, path)
        if obj is not None:
            if allow_list and isinstance(obj, list):
                for x in obj:
                    c[str(x)] += 1
            elif not allow_list:
                c[str(obj)] += 1
    return c


def get_datasets_to_studies(studies):
    """Map dataset_used_standardized -> list of studies that use it."""
    out = defaultdict(list)
    for s in studies:
        ed = s.get("extracted_data") or {}
        for ds in ed.get("datasets_used") or []:
            if isinstance(ds, dict):
                name = ds.get("dataset_used_standardized") or "unknown"
                if name and name != "unknown" and name not in DATASET_EXCLUDE:
                    out[name].append(s)
    return dict(out)


def format_distribution(counter, n, top_n=15):
    """Format counter as lines of '  value: count (pct%)'."""
    if not n or not counter:
        return ["  (no data)"]
    lines = []
    for val, cnt in counter.most_common(top_n):
        pct = 100.0 * cnt / n
        lines.append(f"  {val}: {cnt} ({pct:.1f}%)")
    return lines


def analyze_one_dataset(dataset_name, studies):
    """Return a dict of field -> Counter for this dataset."""
    n = len(studies)
    if n == 0:
        return None, 0

    out = {}
    out["study_type"] = count_field(["study_type"], studies, allow_list=False)
    out["task_type"] = count_field(["task_type"], studies, allow_list=False)
    out["outcomes_modeled"] = count_field(["outcomes_modeled"], studies, allow_list=False)
    out["model_class"] = count_field(["model_class"], studies, allow_list=False)

    # Validation level (derived)
    c_val = Counter()
    for s in studies:
        level = get_validation_level(s.get("extracted_data"))
        c_val[level] += 1
    out["validation_level"] = c_val

    # Modalities (list)
    c_mod = Counter()
    for s in studies:
        for m in (s.get("extracted_data") or {}).get("modalities_used") or []:
            c_mod[m] += 1
    out["modalities_used"] = c_mod

    out["longitudinal_tier"] = count_field(["longitudinal_use", "longitudinal_tier"], studies, allow_list=False)
    out["neuro_onc_domain"] = count_field(["neuro_oncology_domain", "neuro_onc_domain"], studies, allow_list=False)
    out["primary_vs_metastatic"] = count_field(["neuro_oncology_domain", "primary_vs_metastatic"], studies, allow_list=False)
    out["compartment"] = count_field(["neuro_oncology_domain", "compartment"], studies, allow_list=False)
    out["who_family"] = count_field(["neuro_oncology_domain", "who_family"], studies, allow_list=False)

    return out, n


def write_report(datasets_to_studies, output_path):
    """Write per-dataset analysis report to output_path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("=" * 72)
    lines.append("EXTRACTION RESULTS BY DATASET")
    lines.append("=" * 72)
    lines.append(f"Input: studies_with_extracted_data.jsonl")
    lines.append(f"Datasets: {len(datasets_to_studies)} (excluding 'other')")
    lines.append("")

    # Sort by number of studies descending
    order = sorted(datasets_to_studies.keys(), key=lambda d: len(datasets_to_studies[d]), reverse=True)

    for dataset_name in order:
        studies = datasets_to_studies[dataset_name]
        stats, n = analyze_one_dataset(dataset_name, studies)
        if stats is None:
            continue

        lines.append("")
        lines.append("-" * 72)
        lines.append(f"DATASET: {dataset_name}  (n = {n} studies)")
        lines.append("-" * 72)

        field_labels = [
            ("study_type", "Study type"),
            ("task_type", "Task type"),
            ("outcomes_modeled", "Outcomes modeled"),
            ("model_class", "Model class"),
            ("validation_level", "Validation level"),
            ("modalities_used", "Modalities used"),
            ("longitudinal_tier", "Longitudinal tier"),
            ("neuro_onc_domain", "Neuro-oncology domain"),
            ("primary_vs_metastatic", "Primary vs metastatic"),
            ("compartment", "Compartment"),
            ("who_family", "WHO tumor family"),
        ]
        for key, label in field_labels:
            c = stats.get(key) or Counter()
            lines.append(f"\n  {label}:")
            lines.extend(format_distribution(c, n, top_n=20))

        lines.append("")

    lines.append("")
    lines.append("=" * 72)
    lines.append("END OF REPORT")
    lines.append("=" * 72)

    text = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(text)
    print(f"Report written to {output_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze extraction results per dataset")
    parser.add_argument("--input", default=str(INPUT_FILE), help="Studies with extracted data (JSONL)")
    parser.add_argument("--output", default=str(OUTPUT_FILE), help="Output report path")
    parser.add_argument("--include-other", action="store_true", help="Include dataset 'other' in breakdown")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        print("Run extraction_2_process_results.py first.")
        return

    studies = []
    with open(input_path, "r") as f:
        for line in f:
            studies.append(json.loads(line))
    print(f"Loaded {len(studies)} studies from {input_path}")

    global DATASET_EXCLUDE
    if args.include_other:
        DATASET_EXCLUDE = set()

    datasets_to_studies = get_datasets_to_studies(studies)
    total_mentions = sum(len(s) for s in datasets_to_studies.values())
    print(f"Found {len(datasets_to_studies)} datasets, {total_mentions} dataset mentions (studies can use multiple)")

    write_report(datasets_to_studies, output_path)


if __name__ == "__main__":
    main()
