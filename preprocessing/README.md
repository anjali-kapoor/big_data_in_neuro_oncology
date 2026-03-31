# Preprocessing

Scripts for converting bibliographic exports to RIS (if needed) and merging/deduplicating references.

## Scripts

| Script | Role |
|--------|------|
| `pubmedToRis.py` | Converts PubMed plain-text exports to RIS (usage: see module docstring). |
| `ris_import_deduplicate.py` | Reads `pubmed_txt/*.ris`, merges records, filters to complete entries, deduplicates, writes CSV (and combined RIS) in this directory. **Run from `preprocessing/`.** |

## Typical sequence

1. Place `.ris` files in `pubmed_txt/` (or change the folder list in `ris_import_deduplicate.py`).
2. From `preprocessing/`:

   ```bash
   python ris_import_deduplicate.py
   ```

   Produces `all_references_without_duplicates.csv` here.

3. From the **repository root**:

   ```bash
   python main_workflow/0_csv_to_jsonl.py
   ```

   Reads `preprocessing/all_references_without_duplicates.csv` and writes `preprocessing/deduped_and_processed_studies.jsonl`.

Input corpora are supplied by the user; they are not part of this repository.
