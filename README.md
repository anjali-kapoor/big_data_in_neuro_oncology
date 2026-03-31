# Neuro-oncology literature pipeline — supplementary code

This repository supports reproducibility of the methods in the associated publication: processing bibliographic records through **deduplication**, **LLM-based screening** for analytical use of prespecified data resources, **structured extraction** with schema-validated outputs, and **optional summary analyses**.

Primary corpora (bibliographic exports, JSONL study files, and model API responses) are **not** included; reviewers can inspect program logic, prompts, and schemas here.

## Pipeline (high level)

| Stage | Description |
|--------|-------------|
| **Preprocessing** | Import references (e.g., PubMed/RIS), deduplicate, normalize to JSONL. |
| **Screening** | Classify whether each abstract describes cohort-level analytical use of a target dataset (rules and allowlist in `Prompts/dataset_screening_instructions.txt`). |
| **Extraction** | For included studies, fill structured fields defined in `main_workflow/schemas.py` under instructions in `Prompts/extraction_instructions.txt`. |
| **Analysis** | Optional scripts: per-dataset summary tables (`analyze_extraction_by_dataset.py`); diversity metrics (`dataset_diversity_analysis.py`). |

## Layout

| Path | Contents |
|------|----------|
| `preprocessing/` | Reference import and deduplication scripts |
| `main_workflow/` | Screening and extraction batch preparation, result merging, schemas, batch API helper, analysis scripts |
| `Prompts/` | Screening and extraction instructions |
| `documentation/` | Pipeline narrative and field documentation for reviewers |

## Requirements

- Python 3.10+
- Install: `pip install -r requirements.txt`
- Environment variable `OPENAI_API_KEY` for OpenAI Batch API calls

## Run order

Execute from the repository root. Before downloading batch jobs, create the output directory once:

```bash
mkdir -p "Batch Responses"
```

**1. Preprocessing** — See `preprocessing/README.md`. After `preprocessing/all_references_without_duplicates.csv` exists:

```bash
python main_workflow/0_csv_to_jsonl.py
```

**2. Screening**

```bash
python main_workflow/screening_1_prepare_batch.py
python main_workflow/batch_api_helpers.py submit screening_batch_requests.jsonl
python main_workflow/batch_api_helpers.py wait <batch_id>
python main_workflow/batch_api_helpers.py download <batch_id> "Batch Responses/screening_output.jsonl"
python main_workflow/screening_2_process_results.py
```

**3. Extraction**

```bash
python main_workflow/extraction_1_prepare_batch.py
python main_workflow/batch_api_helpers.py submit data_extraction_batch_requests.jsonl
python main_workflow/batch_api_helpers.py wait <batch_id>
python main_workflow/batch_api_helpers.py download <batch_id> "Batch Responses/data_extraction_output.jsonl"
python main_workflow/extraction_2_process_results.py
```

**4. Analysis (optional)**

```bash
python main_workflow/analyze_extraction_by_dataset.py
python main_workflow/dataset_diversity_analysis.py
```

## Reproducibility notes

- The screening **target dataset list** and eligibility rules live in **`Prompts/dataset_screening_instructions.txt`**.
- Extraction **structure and allowed literals** are defined in **`main_workflow/schemas.py`** and mirrored in the prompts.
- **Model identifier and reasoning settings** are set in `screening_1_prepare_batch.py` and `extraction_1_prepare_batch.py` and should correspond to the manuscript.

## Documentation for reviewers

| File | Purpose |
|------|---------|
| `documentation/PIPELINE.md` | Data flow, intermediate files, and stage descriptions |
| `documentation/SCHEMA_REFERENCE.md` | Extraction fields (overview) |
| `documentation/FIELD_REFERENCE.md` | Field definitions and rationale |
| `documentation/SUPPLEMENTAL_SCHEMA_TABLES.md` | Tabular schema summary (supplement-aligned) |

## License

See `LICENSE`.
