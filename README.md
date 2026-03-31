# Neuro-oncology literature pipeline (publication code)

Minimal, reproducible **code skeleton** for the workflow:

**PubMed / RIS → preprocessing → LLM screening → structured extraction → analysis**

This repository intentionally **excludes**: plotting scripts, auxiliary experiments (e.g. free-form dataset naming), raw or processed study files (JSONL/CSV/RIS), and one-off debugging utilities.

## What is included

| Stage | Contents |
|--------|----------|
| **Preprocessing** | `preprocessing/` — PubMed→RIS, RIS dedup to CSV, optional term filter; `main_workflow/0_csv_to_jsonl.py` — CSV → JSONL for screening |
| **Screening** | `screening_1_prepare_batch.py`, `screening_2_process_results.py`, `Prompts/dataset_screening_instructions.txt`, `Prompts/target_datasets.txt` |
| **Extraction** | `extraction_1_prepare_batch.py`, `extraction_2_process_results.py`, `Prompts/extraction_instructions.txt`, `schemas.py` |
| **Batch API** | `batch_api_helpers.py` — submit, wait, download OpenAI Batch jobs |
| **Analysis** | `analyze_extraction_by_dataset.py` (text report), `dataset_diversity_analysis.py` (entropy metrics to stdout) |
| **Docs** | `documentation/` — workflow narrative and schema references |

## Requirements

- Python 3.10+
- `OPENAI_API_KEY` in the environment for Batch API calls

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run order (from repository root)

Paths below match this repo layout (`publication_code/` = root).

### 1. Build `deduped_and_processed_studies.jsonl`

See `preprocessing/README.md`. You must supply your own PubMed/RIS inputs.

```bash
python main_workflow/0_csv_to_jsonl.py
```

### 2. Screening

```bash
python main_workflow/screening_1_prepare_batch.py
python main_workflow/batch_api_helpers.py submit screening_batch_requests.jsonl
python main_workflow/batch_api_helpers.py wait <batch_id>
python main_workflow/batch_api_helpers.py download <batch_id> "Batch Responses/screening_output.jsonl"
python main_workflow/screening_2_process_results.py
```

Produces (by default, next to repo root): `screened_studies.jsonl`, `included_studies.jsonl`, `excluded_studies_minimal.jsonl`.

### 3. Extraction

```bash
python main_workflow/extraction_1_prepare_batch.py
python main_workflow/batch_api_helpers.py submit data_extraction_batch_requests.jsonl
python main_workflow/batch_api_helpers.py wait <batch_id>
python main_workflow/batch_api_helpers.py download <batch_id> "Batch Responses/data_extraction_output.jsonl"
python main_workflow/extraction_2_process_results.py
```

Produces `studies_with_extracted_data.jsonl` (merged structured fields).

### 4. Analysis (optional)

```bash
python main_workflow/analyze_extraction_by_dataset.py
python main_workflow/dataset_diversity_analysis.py
```

## Configuration

- Edit **`Prompts/target_datasets.txt`** before screening so the model knows which registry/clinical/omics resources count as in-scope “datasets” for your review.
- Model IDs and reasoning effort are set in the `*_prepare_batch.py` scripts (defaults match the original project; change if you cite a different model in the paper).

## Schema

Pydantic models live in **`main_workflow/schemas.py`**. Human-readable field tables: **`documentation/SCHEMA_REFERENCE.md`**, **`documentation/FIELD_REFERENCE.md`**, **`documentation/SUPPLEMENTAL_SCHEMA_TABLES.md`**.

## Full narrative

Step-by-step description (including paths and batch commands) is in **`documentation/COMPLETE_WORKFLOW.md`**. Treat the repository root as the directory containing `main_workflow/` and `preprocessing/`.

## Push to GitHub

This folder is already a git repository with an initial commit on **`main`**. After you add a remote:

```bash
cd publication_code   # or the path where you keep this clone
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```

Create an empty repository on GitHub first (no README/license if you are pushing this existing history), or use `gh repo create`. If you copied only the files without `.git`, run `git init` and `git add` / `git commit` once, then add the remote.

Before screening/extraction downloads, create the batch output folder once:

```bash
mkdir -p "Batch Responses"
```

## License

Add your lab’s preferred license before publishing the GitHub repository.
