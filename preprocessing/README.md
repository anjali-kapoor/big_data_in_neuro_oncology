# Preprocessing

Scripts for converting PubMed exports to RIS, deduplicating references, and (optionally) filtering abstracts by search terms.

## Layout

- `pubmedToRis.py` — PubMed plain-text → RIS (run with your input/output paths; see script docstring).
- `ris_import_deduplicate.py` — Reads `pubmed_txt/*.ris`, merges, filters complete records, deduplicates, writes CSV and combined RIS **in this directory** (run from `preprocessing/`).
- `pubmed_txt/extract_abstracts_by_terms.py` — Optional helper to pull lines matching terms from large PubMed text files.

## Typical flow

1. Place `.ris` files under `pubmed_txt/` (or adjust folder list inside `ris_import_deduplicate.py`).
2. From the **`preprocessing/`** directory:

   ```bash
   python ris_import_deduplicate.py
   ```

   Produces `all_references_without_duplicates.csv` in `preprocessing/`.

3. From the **repository root** (`publication_code/`):

   ```bash
   python main_workflow/0_csv_to_jsonl.py
   ```

   Expects `preprocessing/all_references_without_duplicates.csv` and writes `preprocessing/deduped_and_processed_studies.jsonl`.

Do not commit CSV/JSONL/RIS; add your own data locally.
