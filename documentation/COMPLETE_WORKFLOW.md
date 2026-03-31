# Complete Workflow: Literature Search to Data Extraction

End-to-end pipeline from PubMed/RIS files to structured neuro-oncology data.

## File Organization

### Phase 0: Preprocessing (Your Existing Scripts)
```
ris_import_deduplicate.py    ← Keep, use as-is
pubmedToRis.py                ← Keep if needed
```

### Phase 0.5: Format Conversion (New Script)
```
0_csv_to_jsonl.py             ← NEW - bridges preprocessing to screening
```

### Phase 1: Screening (New Scripts)
```
schemas.py                    ← REPLACES batching.py
screening_1_prepare_batch.py  ← New
screening_2_process_results.py ← New
```

### Phase 2: Extraction (New Scripts)
```
extraction_1_prepare_batch.py ← REPLACES openai.py
extraction_2_process_results.py ← New
```

### Utilities
```
batch_api_helpers.py          ← Batch API management
```

## Complete Pipeline

### Step 0: Literature Search & Import

**If you have PubMed files:**
```bash
# Convert PubMed to RIS (if needed)
python pubmedToRis.py
```

**Deduplicate RIS files:**
```bash
python ris_import_deduplicate.py
```

**Output:** `all_references_without_duplicates.csv`

**What it does:**
- Reads RIS files from `pubmed_txt/` folder
- Filters for complete records (title, authors, year, abstract, DOI)
- Deduplicates by DOI and title
- Creates CSV with columns: title, authors, year, abstract, doi

---

### Step 1: Convert CSV to JSONL

```bash
python 0_csv_to_jsonl.py
```

**Input:** `all_references_without_duplicates.csv`  
**Output:** `deduped_and_processed_studies.jsonl`

**What it does:**
- Converts CSV to JSONL format
- Standardizes field names (title → Title, abstract → Abstract)
- Drops studies without title or abstract
- Each line is a JSON object: `{"Title": "...", "Abstract": "...", "Year": "...", ...}`

---

### Step 2: Screen for Dataset Analytics

```bash
# Prepare batch
python screening_1_prepare_batch.py
```

**Output:** `screening_batch_requests.jsonl`

```bash
# Submit to OpenAI
python batch_api_helpers.py submit screening_batch_requests.jsonl
# Save the batch ID!

# Wait for completion
python batch_api_helpers.py wait batch_xxxxx

# Download results
python batch_api_helpers.py download batch_xxxxx "Batch Responses/screening_output.jsonl"
```

```bash
# Process results
python screening_2_process_results.py
```

**Outputs:**
- `screened_studies.jsonl` - All studies with decisions
- `included_studies.jsonl` - Only analytical use = "yes"
- `excluded_studies_minimal.jsonl` - Minimal data for excluded

**What it does:**
- Screens each study for analytical use of datasets
- Categories: yes (include), no (exclude), unclear
- Excludes: biospecimen_only, wet_lab_only, narrative, descriptive, methods papers
- Records minimal data for excluded studies (title, year, dataset, reason)

---

### Step 3: Extract Structured Data

```bash
# Prepare extraction batch
python extraction_1_prepare_batch.py
```

**Input:** `included_studies.jsonl`  
**Output:** `data_extraction_batch_requests.jsonl`

```bash
# Submit to OpenAI
python batch_api_helpers.py submit data_extraction_batch_requests.jsonl

# Wait and download (same as step 2)
python batch_api_helpers.py wait batch_yyyyy
python batch_api_helpers.py download batch_yyyyy "Batch Responses/data_extraction_output.jsonl"
```

```bash
# Process extraction results
python extraction_2_process_results.py
```

**Output:** `studies_with_extracted_data.jsonl`

**What it extracts:**
- Basic metadata (title, year, journal)
- Study type, datasets used, task type
- Model class, modalities, validation strategy
- Longitudinal use (4-tier classification)
- Neuro-oncology domain (WHO family, compartment, etc.)

---

## File Flow Diagram

```
Literature Search (PubMed, Scopus, etc.)
    ↓
[Optional: pubmedToRis.py]
    ↓
RIS files in pubmed_txt/
    ↓
ris_import_deduplicate.py
    ↓
all_references_without_duplicates.csv (e.g., 10,000 papers)
    ↓
0_csv_to_jsonl.py
    ↓
deduped_and_processed_studies.jsonl
    ↓
screening_1_prepare_batch.py
    ↓
screening_batch_requests.jsonl
    ↓
[OpenAI Batch API - Screening]
    ↓
Batch Responses/screening_output.jsonl
    ↓
screening_2_process_results.py
    ↓
├─ screened_studies.jsonl (all 10,000)
├─ included_studies.jsonl (e.g., 500 included)
└─ excluded_studies_minimal.jsonl (e.g., 9,500 excluded)
    ↓
extraction_1_prepare_batch.py (uses included_studies.jsonl)
    ↓
data_extraction_batch_requests.jsonl
    ↓
[OpenAI Batch API - Extraction]
    ↓
Batch Responses/data_extraction_output.jsonl
    ↓
extraction_2_process_results.py
    ↓
studies_with_extracted_data.jsonl (500 with full structured data)
```

---

## What Changed from Your Old Workflow

### Old Workflow (batching.py + openai.py)
```
RIS → CSV → JSONL → Extraction (all papers, old schema)
```

**Issues:**
- No screening step (extracted from ALL papers)
- Used old medical LLM schema (ACGME specialties)
- Expensive (extracts from all papers)

### New Workflow (My Scripts)
```
RIS → CSV → JSONL → Screening → Extraction (only included, neuro schema)
```

**Benefits:**
- ✅ Screens first (cheaper, more focused)
- ✅ Neuro-oncology specific schema
- ✅ Minimal data for excluded papers
- ✅ Longitudinal modeling tiers
- ✅ WHO tumor classifications

---

## Migration Guide

### What to Keep
```
✅ ris_import_deduplicate.py    - Still needed for preprocessing
✅ pubmedToRis.py                - Keep if you use it
```

### What to Replace
```
❌ batching.py          → ✅ schemas.py (new neuro-oncology schema)
❌ openai.py            → ✅ extraction_1_prepare_batch.py (new extraction)
```

### What to Add
```
+ 0_csv_to_jsonl.py               (bridge script)
+ screening_1_prepare_batch.py    (new screening)
+ screening_2_process_results.py  (new screening)
+ extraction_2_process_results.py (new extraction processing)
+ batch_api_helpers.py            (utilities)
```

---

## Folder Structure

```
project/
├── pubmed_txt/                          # Your RIS files
│   ├── search1.ris
│   ├── search2.ris
│   └── ...
│
├── Prompts/
│   ├── dataset_screening_instructions.txt   # includes TARGET DATASETS list
│   └── extraction_instructions.txt
│
├── Batch Responses/                     # Create this folder
│   ├── screening_output.jsonl
│   └── data_extraction_output.jsonl
│
├── preprocessing scripts:
│   ├── pubmedToRis.py                   (your existing)
│   ├── ris_import_deduplicate.py        (your existing)
│   └── 0_csv_to_jsonl.py                (new bridge)
│
├── screening scripts:
│   ├── schemas.py                       (replaces batching.py)
│   ├── screening_1_prepare_batch.py
│   └── screening_2_process_results.py
│
├── extraction scripts:
│   ├── extraction_1_prepare_batch.py    (replaces openai.py)
│   └── extraction_2_process_results.py
│
├── utilities:
│   └── batch_api_helpers.py
│
└── outputs:
    ├── all_references_with_duplicates.ris
    ├── all_references_without_duplicates.csv
    ├── deduped_and_processed_studies.jsonl
    ├── screening_batch_requests.jsonl
    ├── screened_studies.jsonl
    ├── included_studies.jsonl
    ├── excluded_studies_minimal.jsonl
    ├── data_extraction_batch_requests.jsonl
    └── studies_with_extracted_data.jsonl
```

---

## Quick Start from Your Current State

If you already have `all_references_without_duplicates.csv`:

```bash
# 1. Convert to JSONL
python 0_csv_to_jsonl.py

# 2. (Optional) Edit TARGET DATASETS in Prompts/dataset_screening_instructions.txt

# 3. Run screening
python screening_1_prepare_batch.py
python batch_api_helpers.py submit screening_batch_requests.jsonl
# ... wait for batch ...
python batch_api_helpers.py download batch_xxxxx "Batch Responses/screening_output.jsonl"
python screening_2_process_results.py

# 4. Run extraction
python extraction_1_prepare_batch.py
python batch_api_helpers.py submit data_extraction_batch_requests.jsonl
# ... wait for batch ...
python batch_api_helpers.py download batch_yyyyy "Batch Responses/data_extraction_output.jsonl"
python extraction_2_process_results.py

# Done! Check studies_with_extracted_data.jsonl
```

---

## Cost Comparison

### Old Method (Extract from All)
- 10,000 papers × 1,000 tokens/paper = 10M tokens
- Cost: ~$100

### New Method (Screen then Extract)
- Screening: 10,000 papers × 300 tokens = 3M tokens → $15
- Extraction: 500 papers × 1,000 tokens = 500K tokens → $5
- **Total: $20 (80% savings!)**

---

## Summary

**Your existing files are PREPROCESSING steps** that feed into my new screening/extraction workflow.

**Complete order:**
1. ✅ `ris_import_deduplicate.py` (keep)
2. ✅ `0_csv_to_jsonl.py` (new bridge)
3. ✅ Screening (new workflow)
4. ✅ Extraction (new workflow with neuro-oncology schema)

**Archive these:**
- ❌ `batching.py` (old schema)
- ❌ `openai.py` (old extraction without screening)
