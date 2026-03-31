# Pipeline: data flow and artifacts

This document summarizes how records move through preprocessing, screening, extraction, and optional analysis. Paths are relative to the repository root.

## 1. Preprocessing

**Inputs:** RIS files placed under `preprocessing/pubmed_txt/` (or paths adjusted in `ris_import_deduplicate.py`). Optional: PubMed plain-text converted with `preprocessing/pubmedToRis.py`.

**Steps:**

1. Run `ris_import_deduplicate.py` from the `preprocessing/` directory. It merges RIS records, requires complete bibliographic fields (including abstract and DOI where applicable), deduplicates by DOI and title, and writes:
   - `preprocessing/all_references_without_duplicates.csv`
2. Run `main_workflow/0_csv_to_jsonl.py` from the repository root. It reads the CSV and writes:
   - `preprocessing/deduped_and_processed_studies.jsonl`  
   One JSON object per line, with standardized keys (e.g., `Title`, `Abstract`, `Year`, `DOI`, `Authors`).

## 2. Screening

**Input:** `preprocessing/deduped_and_processed_studies.jsonl`

**Prompt:** `Prompts/dataset_screening_instructions.txt` (includes the target dataset allowlist and inclusion/exclusion criteria).

**Steps:**

1. `screening_1_prepare_batch.py` builds batch requests with structured outputs conforming to `ScreeningDecision` in `schemas.py`, and writes `screening_batch_requests.jsonl` at the repository root.
2. Requests are submitted and completed via the OpenAI Batch API (`batch_api_helpers.py`). Results are saved as `Batch Responses/screening_output.jsonl`.
3. `screening_2_process_results.py` merges responses with the original records and writes:
   - `screened_studies.jsonl` — all studies with screening fields  
   - `included_studies.jsonl` — studies classified as analytical use of a target dataset  
   - `excluded_studies_minimal.jsonl` — reduced fields for excluded studies  

## 3. Extraction

**Input:** `included_studies.jsonl`

**Prompt:** `Prompts/extraction_instructions.txt`  
**Schema:** `Extraction` and nested models in `schemas.py`

**Steps:**

1. `extraction_1_prepare_batch.py` writes `data_extraction_batch_requests.jsonl`.
2. Batch completion and download to `Batch Responses/data_extraction_output.jsonl`.
3. `extraction_2_process_results.py` merges model outputs into full study records:
   - `studies_with_extracted_data.jsonl`

## 4. Analysis (optional)

- **`analyze_extraction_by_dataset.py`** — Aggregates counts and distributions of key extracted fields by standardized dataset name; writes a text report (default path under `reports/` relative to the working directory used in the script).
- **`dataset_diversity_analysis.py`** — Computes normalized entropy–based diversity metrics for study type and task type by dataset; prints results to standard output.

## Data flow (summary)

```
RIS / bibliographic CSV
  → all_references_without_duplicates.csv
  → deduped_and_processed_studies.jsonl
  → [Batch API: screening] → screened / included / excluded JSONL
  → [Batch API: extraction] → studies_with_extracted_data.jsonl
  → [optional analysis scripts]
```

Artifact names above match the defaults in the provided scripts; local paths can be overridden via command-line arguments where implemented.
