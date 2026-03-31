# Neuro-oncology literature pipeline — supplementary code

This code was developed for and used in a **narrative review of Big Data in Neuro-Oncology**. It provides a reproducible pattern for **automated LLM screening and structured extraction** of bibliographic records—typically titles and abstracts from PubMed or similar exports—at scale via batch APIs, with inclusion rules and extraction fields defined in prompts and Pydantic schemas. The same workflow can be adapted to other review questions or disease areas by editing those prompts and models.

This repository supports reproducibility of those methods: processing bibliographic records through **deduplication**, **LLM-based screening** for analytical use of prespecified data resources, **structured extraction** with schema-validated outputs, and **optional summary analyses**.

## Pipeline (high level)

| Stage | Description |
|--------|-------------|
| **Preprocessing** | Import references (e.g., PubMed/RIS), deduplicate, normalize to JSONL. |
| **Screening** | Classify whether each abstract describes cohort-level analytical use of a target dataset (rules and allowlist in `Prompts/dataset_screening_instructions.txt`). |
| **Extraction** | For included studies, fill structured fields defined in `main_workflow/schemas.py` under instructions in `Prompts/extraction_instructions.txt`. |
| **Analysis** | Optional: per-dataset summary tables (`analyze_extraction_by_dataset.py`). |

## Layout

| Path | Contents |
|------|----------|
| `preprocessing/` | Reference import and deduplication scripts |
| `main_workflow/` | Screening and extraction batch preparation, result merging, schemas, batch API helper, analysis scripts |
| `Prompts/` | Screening and extraction instructions |

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
```

## Reproducibility notes

- The screening **target dataset list** and eligibility rules live in **`Prompts/dataset_screening_instructions.txt`**.
- Extraction **structure and allowed literals** are defined in **`main_workflow/schemas.py`** and mirrored in the prompts.
- **Model identifier and reasoning settings** are set in `screening_1_prepare_batch.py` and `extraction_1_prepare_batch.py` and should correspond to the manuscript.

## Field definitions and screening rules

Machine-readable extraction constraints are in **`main_workflow/schemas.py`**. Natural-language instructions and the screening target-dataset allowlist are in **`Prompts/extraction_instructions.txt`** and **`Prompts/dataset_screening_instructions.txt`**.

