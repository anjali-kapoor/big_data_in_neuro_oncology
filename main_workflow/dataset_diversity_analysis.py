"""
Compute dataset diversity in terms of study_type and task_type.

METRIC:
  - Normalized Shannon entropy: H_norm = H / log2(k)
    where H = -sum(p * log2(p)) is Shannon entropy, k = number of categories.
  - Range: 0 (all studies in one category) to 1 (perfectly uniform across categories).
  - Combined diversity = average of study_type normalized entropy and task_type normalized entropy.

  This is a standard information-theory metric; "combined diversity" is our name for
  averaging it across study_type and task_type.
"""

import json
import math
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "studies_with_extracted_data.jsonl"
DATASET_EXCLUDE = {"other", "unknown"}


def load_studies(path):
    studies = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            studies.append(json.loads(line))
    return studies


def get_datasets_to_studies(studies):
    out = defaultdict(list)
    for s in studies:
        ed = s.get("extracted_data") or {}
        for ds in ed.get("datasets_used") or []:
            if isinstance(ds, dict):
                name = ds.get("dataset_used_standardized") or "unknown"
                if name and name not in DATASET_EXCLUDE:
                    out[name].append(s)
    return dict(out)


def entropy(counter):
    """Shannon entropy: -sum(p * log2(p)). Higher = more diverse."""
    n = sum(counter.values())
    if n <= 0:
        return 0.0
    h = 0
    for c in counter.values():
        if c > 0:
            p = c / n
            h -= p * math.log2(p)
    return h


def normalized_entropy(counter):
    """Entropy / max_entropy. 1 = uniform, 0 = single category."""
    n = sum(counter.values())
    if n <= 0:
        return 0.0
    k = len(counter)
    if k <= 1:
        return 0.0
    max_h = math.log2(k)
    return entropy(counter) / max_h


def main():
    studies = load_studies(INPUT_FILE)
    d2s = get_datasets_to_studies(studies)

    # Compute diversity for each dataset (include all; min 5 for detailed breakdown)
    MIN_STUDIES = 5
    results = []

    for ds_name, studies_list in d2s.items():

        study_type_counts = Counter()
        task_type_counts = Counter()
        for s in studies_list:
            ed = s.get("extracted_data") or {}
            st = ed.get("study_type")
            tt = ed.get("task_type")
            if st:
                study_type_counts[st] += 1
            if tt:
                task_type_counts[tt] += 1

        ne_st = normalized_entropy(study_type_counts) if study_type_counts else 0
        ne_tt = normalized_entropy(task_type_counts) if task_type_counts else 0
        # Combined diversity: average of the two normalized entropies
        combined = (ne_st + ne_tt) / 2 if (study_type_counts or task_type_counts) else 0

        n_study_types = len(study_type_counts)
        n_task_types = len(task_type_counts)

        results.append({
            "dataset": ds_name,
            "n_studies": len(studies_list),
            "n_study_types": n_study_types,
            "n_task_types": n_task_types,
            "study_type_entropy": ne_st,
            "task_type_entropy": ne_tt,
            "combined_diversity": combined,
            "study_type_dist": dict(study_type_counts.most_common()),
            "task_type_dist": dict(task_type_counts.most_common()),
        })

    # Sort by combined diversity (desc)
    results.sort(key=lambda x: (-x["combined_diversity"], -x["n_studies"]))

    print("=" * 80)
    print("DATASET DIVERSITY: Study type & Task type (normalized entropy)")
    print("Higher = more evenly split across categories. Min 5 studies per dataset.")
    print("=" * 80)

    for r in results[:25]:
        if r["n_studies"] < MIN_STUDIES:
            continue  # skip detailed breakdown for small n
        print(f"\n{r['dataset']} (n={r['n_studies']})")
        print(f"  Combined diversity: {r['combined_diversity']:.3f}")
        print(f"  Study type entropy: {r['study_type_entropy']:.3f}  ({r['n_study_types']} categories)")
        print(f"  Task type entropy:  {r['task_type_entropy']:.3f}  ({r['n_task_types']} categories)")
        print(f"  Study types: {r['study_type_dist']}")
        print(f"  Task types:  {r['task_type_dist']}")

    print("\n" + "=" * 80)
    print("TOP 10 MOST DIVERSE (by combined entropy):")
    for i, r in enumerate(results[:10], 1):
        print(f"  {i}. {r['dataset']}: {r['combined_diversity']:.3f} (n={r['n_studies']})")

    print("\n" + "=" * 80)
    print("COMBINED DIVERSITY FOR EVERY DATASET (sorted by diversity desc):")
    for r in results:
        print(f"  {r['dataset']}: {r['combined_diversity']:.3f}  (n={r['n_studies']})")


if __name__ == "__main__":
    main()
