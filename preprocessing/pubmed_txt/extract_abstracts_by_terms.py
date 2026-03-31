#!/usr/bin/env python3
"""
Extract abstracts from abstract-braintumor-full.txt that contain specific terms.
Creates 4 files (with classified outcome appended from studies_with_extracted_data.jsonl):
  - abstracts_quality_of_life.txt
  - abstracts_functional_or_neurological_outcome.txt
  - abstracts_recurrence.txt
  - abstracts_progression_free_survival.txt
"""
import json
import re
from pathlib import Path

INPUT_FILE = Path(__file__).resolve().parent / "abstract-braintumor-full.txt"
OUTPUT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = OUTPUT_DIR.parent.parent
EXTRACTED_JSONL = PROJECT_ROOT / "studies_with_extracted_data.jsonl"

# (output filename, list of phrases; abstract included if it contains ANY phrase)
FILTERS = [
    ("abstracts_quality_of_life.txt", ["quality of life"]),
    ("abstracts_functional_or_neurological_outcome.txt", ["functional outcome", "neurological outcome"]),
    ("abstracts_recurrence.txt", ["recurrence"]),
    ("abstracts_progression_free_survival.txt", ["progression-free survival"]),
]


def is_abstract_start(line: str) -> bool:
    """True if line starts abstract (e.g. '1. Neuro Oncol.')."""
    return bool(re.match(r"^\d+\.\s+[A-Z]", line))


def _normalize(t: str) -> str:
    """Collapse whitespace and lower for matching."""
    if not t:
        return ""
    return " ".join(str(t).split()).lower()


def _format_outcome(outcomes_modeled) -> str:
    """Format outcome(s) for display."""
    if outcomes_modeled is None:
        return "none_or_not_applicable"
    if isinstance(outcomes_modeled, list):
        return ", ".join(str(x) for x in outcomes_modeled)
    return str(outcomes_modeled)


def load_title_to_outcome():
    """Load studies_with_extracted_data.jsonl; return list of (normalized_title, outcome_str) sorted by title length desc for best match."""
    if not EXTRACTED_JSONL.exists():
        return []
    out = []
    with open(EXTRACTED_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ed = d.get("extracted_data") or {}
            title = d.get("Title") or ""
            outcome = _format_outcome(ed.get("outcomes_modeled"))
            out.append((_normalize(title), outcome))
    # Longest title first so we match more specific title when multiple could match
    out.sort(key=lambda x: -len(x[0]))
    return out


def find_classified_outcome(block_text: str, title_to_outcome: list) -> str:
    """Find first (longest) study whose normalized title appears in normalized block."""
    norm_block = _normalize(block_text)
    for norm_title, outcome in title_to_outcome:
        if len(norm_title) < 10:  # skip very short titles to avoid false matches
            continue
        if norm_title in norm_block:
            return outcome
    return "(not in extracted set)"


def main():
    if not INPUT_FILE.exists():
        print(f"Not found: {INPUT_FILE}")
        return

    title_to_outcome = load_title_to_outcome()
    print(f"Loaded {len(title_to_outcome)} studies for outcome lookup.")

    # Open output files
    outs = {}
    for name, _ in FILTERS:
        path = OUTPUT_DIR / name
        outs[name] = open(path, "w", encoding="utf-8")

    current_lines = []
    total_abstracts = 0
    counts = {name: 0 for name, _ in FILTERS}

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if is_abstract_start(line) and current_lines:
                # Finish previous abstract
                total_abstracts += 1
                text = "".join(current_lines)
                text_lower = text.lower()
                for name, phrases in FILTERS:
                    if any(p.lower() in text_lower for p in phrases):
                        outcome_str = find_classified_outcome(text, title_to_outcome)
                        if outcome_str == "(not in extracted set)":
                            continue  # skip abstracts that didn't pass screening
                        counts[name] += 1
                        out = outs[name]
                        for l in current_lines:
                            out.write(l)
                        out.write("Classified outcome(s): ")
                        out.write(outcome_str)
                        out.write("\n\n\n")
                current_lines = []

            current_lines.append(line)

        # Last abstract
        if current_lines:
            total_abstracts += 1
            text = "".join(current_lines)
            text_lower = text.lower()
            for name, phrases in FILTERS:
                if any(p.lower() in text_lower for p in phrases):
                    outcome_str = find_classified_outcome(text, title_to_outcome)
                    if outcome_str == "(not in extracted set)":
                        continue
                    counts[name] += 1
                    out = outs[name]
                    for l in current_lines:
                        out.write(l)
                    out.write("Classified outcome(s): ")
                    out.write(outcome_str)
                    out.write("\n\n\n")

    for name in outs:
        outs[name].close()

    print(f"Processed {total_abstracts} abstracts.")
    for name, phrases in FILTERS:
        print(f"  {name}: {counts[name]} abstracts (phrases: {phrases})")


if __name__ == "__main__":
    main()
