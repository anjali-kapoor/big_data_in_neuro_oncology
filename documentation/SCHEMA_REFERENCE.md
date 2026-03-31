# Schema Reference Guide

Quick reference for the neuro-oncology extraction schema structure.

## Complete Extraction Schema

```json
{
  "title": "string (max 500 chars)",
  "year": "string (max 10 chars)",
  "journal": "string (max 200 chars)",
  
  "study_type": "methodological | clinical_prediction | benchmark_challenge | dataset_description | narrative_review | other | unclear",
  
  "datasets_used": [
    {
      "raw_name": "string (max 200 chars)",
      "dataset_used_standardized": "string (max 200 chars)",
      "role": "primary | secondary | unclear"
    }
  ],
  
  "task_type": "segmentation | detection | classification | survival_prediction | progression_or_recurrence | treatment_response | molecular_prediction | other | unclear",
  
  "outcomes_modeled": "overall_survival | progression_free_survival | recurrence | response | functional_outcome | quality_of_life | complications | cost_utilization | none_or_not_applicable | unclear | other",
  
  "model_class": "traditional_ml | deep_learning | foundation_model | hybrid | unclear",
  
  "modalities_used": [
    "imaging",
    "genomics_or_molecular",
    "pathology",
    "clinical_structured",
    "clinical_text",
    "other"
  ],
  
  "validation_strategy": {
    "internal_validation": "yes | no | unclear",
    "external_validation": "yes | no | unclear",
    "prospective_or_temporal_validation": "yes | no | unclear"
  },
  
  "longitudinal_use": {
    "uses_longitudinal_data": "yes | no | unclear",
    "longitudinal_tier": "0 | 1 | 2 | 3"
  },
  
  "neuro_oncology_domain": {
    "neuro_onc_domain": "adult_primary_brain_tumors | pediatric_brain_tumors | brain_metastases | mixed_or_unspecified",
    "primary_vs_metastatic": "primary | metastatic | both | unclear",
    "compartment": "intra_axial | extra_axial | intraventricular | sellar_suprasellar | cranial_nerve | spinal | leptomeningeal | mixed | unspecified",
    "who_family": "gliomas_glioneuronal_neuronal | ependymal | choroid_plexus | embryonal | pineal | cranial_paraspinal_nerve | meningiomas | mesenchymal_non_meningothelial | melanocytic | hematolymphoid | germ_cell | sellar_region | metastases_to_cns | mixed | unspecified"
  }
}
```

## Field Descriptions

### Basic Metadata

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Full paper title |
| `year` | string | Publication year |
| `journal` | string | Journal name |

### Study Type

Options indicate the primary purpose:
- `methodological`: Novel method/algorithm development
- `clinical_prediction`: Clinical prediction model
- `benchmark_challenge`: Benchmark or challenge paper
- `dataset_description`: Dataset paper
- `narrative_review`: Review article (rare after screening)
- `other`: Doesn't fit above
- `unclear`: Cannot determine

### Datasets Used

Array of dataset objects. Each has:
- `raw_name`: Name as appears in paper
- `dataset_used_standardized`: Matched to target list (or "other")
- `role`: How dataset is used
  - `primary`: Main dataset for analysis
  - `secondary`: Validation, comparison
  - `unclear`: Role not clear

### Task Type

Machine learning task:
- `segmentation`: Tumor/region segmentation
- `detection`: Lesion detection
- `classification`: Categorical prediction (tumor type, grade)
  - **Note**: For molecular alterations, use `molecular_prediction`
- `survival_prediction`: OS or time-to-event
- `progression_or_recurrence`: Disease progression
- `treatment_response`: Response prediction
- `molecular_prediction`: Molecular alteration inference (IDH, MGMT, 1p/19q)
- `other`: Other task
- `unclear`: Cannot determine

### Outcomes Modeled

Primary clinical outcome:
- `overall_survival`: OS
- `progression_free_survival`: PFS
- `recurrence`: Tumor recurrence
- `response`: Treatment response
- `functional_outcome`: Functional status
- `quality_of_life`: QOL measures
- `complications`: Adverse events
- `cost_utilization`: Healthcare costs
- `none_or_not_applicable`: No outcome (e.g., pure segmentation)
- `unclear`: Cannot determine
- `other`: Other outcome

### Model Class

Type of model:
- `traditional_ml`: SVM, random forest, logistic regression
- `deep_learning`: Neural networks, CNNs, transformers
- `foundation_model`: Pre-trained large model
- `hybrid`: Combination of traditional + deep learning
- `unclear`: Cannot determine

### Modalities Used

Data types (array, select all that apply):
- `imaging`: MRI, CT, PET
- `genomics_or_molecular`: Genomic, transcriptomic data
- `pathology`: Histopathology
- `clinical_structured`: Demographics, labs, treatments
- `clinical_text`: Notes, reports
- `other`: Other data types

### Validation Strategy

Three boolean fields:
- `internal_validation`: Cross-validation, train-test split
- `external_validation`: Independent external dataset
- `prospective_or_temporal_validation`: Prospective or temporal cohort

### Longitudinal Use

Two fields:
- `uses_longitudinal_data`: Whether multi-timepoint data is used
- `longitudinal_tier`: Level of longitudinal modeling (0-3)

**Tier Definitions:**

| Tier | Name | Description | Example |
|------|------|-------------|---------|
| 0 | Cross-sectional | Single timepoint, static outcomes | Baseline MRI → tumor grade |
| 1 | Longitudinal outcomes only | Survival modeled, inputs static | Baseline features → OS |
| 2 | Limited longitudinal inputs | ≥2 timepoints, no trajectory | Baseline + 3mo MRI → response |
| 3 | True longitudinal | Time-series, temporal modeling | RNN on serial MRIs |

### Neuro-Oncology Domain

Four related fields:

#### neuro_onc_domain
- `adult_primary_brain_tumors`: Adult gliomas, meningiomas
- `pediatric_brain_tumors`: Pediatric CNS tumors
- `brain_metastases`: CNS metastases
- `mixed_or_unspecified`: Mixed or not specified

#### primary_vs_metastatic
- `primary`: Primary brain tumors
- `metastatic`: Brain metastases
- `both`: Both types
- `unclear`: Cannot determine

#### compartment
Anatomical location:
- `intra_axial`: Brain parenchyma
- `extra_axial`: Meninges, skull base
- `intraventricular`: Ventricles
- `sellar_suprasellar`: Sellar region
- `cranial_nerve`: Cranial nerves
- `spinal`: Spinal cord/column
- `leptomeningeal`: Leptomeningeal
- `mixed`: Multiple compartments
- `unspecified`: Not specified

#### who_family
WHO tumor classification:
- `gliomas_glioneuronal_neuronal`: Gliomas, glioneuronal tumors
- `ependymal`: Ependymomas
- `choroid_plexus`: Choroid plexus tumors
- `embryonal`: Medulloblastoma, etc.
- `pineal`: Pineal tumors
- `cranial_paraspinal_nerve`: Schwannomas, etc.
- `meningiomas`: Meningeal tumors
- `mesenchymal_non_meningothelial`: Mesenchymal
- `melanocytic`: Melanocytic tumors
- `hematolymphoid`: Lymphomas
- `germ_cell`: Germ cell tumors
- `sellar_region`: Pituitary, craniopharyngioma
- `metastases_to_cns`: Metastatic disease
- `mixed`: Multiple types
- `unspecified`: Not specified

## Decision Trees

### Task Type vs Molecular Prediction

```
Is the main task inferring molecular alterations?
├─ YES → molecular_prediction
│         (IDH, MGMT, 1p/19q, etc.)
└─ NO → Is it categorical prediction?
          ├─ YES → classification
          │         (grade, type, subtype)
          └─ NO → Other task type
```

### Longitudinal Tier Selection

```
Does it use multi-timepoint data?
├─ NO → Tier 0 (cross-sectional)
└─ YES → Does it model temporal dynamics?
          ├─ YES → Tier 3 (true longitudinal)
          └─ NO → Does it model survival/time-to-event?
                   ├─ YES, with static inputs → Tier 1
                   └─ NO → Tier 2 (limited longitudinal)
```

### WHO Family for Common Tumors

| Tumor Type | WHO Family |
|------------|------------|
| Glioblastoma | gliomas_glioneuronal_neuronal |
| Astrocytoma | gliomas_glioneuronal_neuronal |
| Oligodendroglioma | gliomas_glioneuronal_neuronal |
| Ependymoma | ependymal |
| Medulloblastoma | embryonal |
| Meningioma | meningiomas |
| Schwannoma | cranial_paraspinal_nerve |
| Pituitary adenoma | sellar_region |
| Brain metastases | metastases_to_cns |

## Example Complete Extractions

### Example 1: Glioma Segmentation

```json
{
  "title": "U-Net for glioblastoma segmentation in BraTS",
  "year": "2024",
  "journal": "Medical Image Analysis",
  "study_type": "methodological",
  "datasets_used": [{
    "raw_name": "BraTS 2021",
    "dataset_used_standardized": "BraTS",
    "role": "primary"
  }],
  "task_type": "segmentation",
  "outcomes_modeled": "none_or_not_applicable",
  "model_class": "deep_learning",
  "modalities_used": ["imaging"],
  "validation_strategy": {
    "internal_validation": "yes",
    "external_validation": "no",
    "prospective_or_temporal_validation": "no"
  },
  "longitudinal_use": {
    "uses_longitudinal_data": "no",
    "longitudinal_tier": "0"
  },
  "neuro_oncology_domain": {
    "neuro_onc_domain": "adult_primary_brain_tumors",
    "primary_vs_metastatic": "primary",
    "compartment": "intra_axial",
    "who_family": "gliomas_glioneuronal_neuronal"
  }
}
```

### Example 2: Multimodal Survival Prediction

```json
{
  "title": "Multimodal survival prediction in glioma using imaging and genomics",
  "year": "2024",
  "journal": "Neuro-Oncology",
  "study_type": "clinical_prediction",
  "datasets_used": [
    {
      "raw_name": "TCGA-GBM",
      "dataset_used_standardized": "TCGA",
      "role": "primary"
    },
    {
      "raw_name": "TCIA glioblastoma",
      "dataset_used_standardized": "TCIA",
      "role": "primary"
    }
  ],
  "task_type": "survival_prediction",
  "outcomes_modeled": "overall_survival",
  "model_class": "hybrid",
  "modalities_used": ["imaging", "genomics_or_molecular", "clinical_structured"],
  "validation_strategy": {
    "internal_validation": "yes",
    "external_validation": "yes",
    "prospective_or_temporal_validation": "no"
  },
  "longitudinal_use": {
    "uses_longitudinal_data": "yes",
    "longitudinal_tier": "1"
  },
  "neuro_oncology_domain": {
    "neuro_onc_domain": "adult_primary_brain_tumors",
    "primary_vs_metastatic": "primary",
    "compartment": "intra_axial",
    "who_family": "gliomas_glioneuronal_neuronal"
  }
}
```

### Example 3: Longitudinal Tumor Growth

```json
{
  "title": "Temporal modeling of glioma growth using serial MRI",
  "year": "2024",
  "journal": "Medical Physics",
  "study_type": "methodological",
  "datasets_used": [{
    "raw_name": "Institutional longitudinal cohort",
    "dataset_used_standardized": "other",
    "role": "primary"
  }],
  "task_type": "progression_or_recurrence",
  "outcomes_modeled": "progression_free_survival",
  "model_class": "deep_learning",
  "modalities_used": ["imaging"],
  "validation_strategy": {
    "internal_validation": "yes",
    "external_validation": "no",
    "prospective_or_temporal_validation": "yes"
  },
  "longitudinal_use": {
    "uses_longitudinal_data": "yes",
    "longitudinal_tier": "3"  // True longitudinal - time-series modeling
  },
  "neuro_oncology_domain": {
    "neuro_onc_domain": "adult_primary_brain_tumors",
    "primary_vs_metastatic": "primary",
    "compartment": "intra_axial",
    "who_family": "gliomas_glioneuronal_neuronal"
  }
}
```

## Validation Rules

The Pydantic schema enforces:
- All Literal fields must match exactly (case-sensitive)
- Arrays can be empty `[]` if information not available
- Nested objects (validation_strategy, longitudinal_use, neuro_oncology_domain) must have all fields
- String length limits are enforced
- "unclear" is always a valid option when information is unavailable
