# Neuro-Oncology Extraction Field Reference

Quick reference for all 40+ extraction fields.

## Basic Metadata (3 fields)

```
title          Paper title (max 500 chars)
year           Publication year (optional)
journal        Journal name (optional)
```

## Study Type (1 field)

```
study_type     methodological | clinical_prediction | benchmark_challenge |
               dataset_description | narrative_review | other | unclear
```

## Datasets Used (array, 3 fields per entry)

```
[{
  raw_name:                    Dataset name as mentioned
  dataset_used_standardized:   Which target dataset (or "other")
  role:                        primary | secondary | unclear
}, ...]
```

## Task & Outcomes (2 fields)

```
task_type          segmentation | detection | classification |
                   survival_prediction | progression_or_recurrence |
                   treatment_response | molecular_prediction |
                   other | unclear

outcomes_modeled   overall_survival | progression_free_survival |
                   recurrence | response | functional_outcome |
                   quality_of_life | complications | cost_utilization |
                   none_or_not_applicable | unclear | other
```

## Model Details (2 fields)

```
model_class        traditional_ml | deep_learning | foundation_model |
                   hybrid | unclear

modalities_used    [imaging, genomics_or_molecular, pathology,
                    clinical_structured, clinical_text, other]
```

## Validation Strategy (3 fields)

```
validation_strategy: {
  internal_validation:                  yes | no | unclear
  external_validation:                  yes | no | unclear
  prospective_or_temporal_validation:   yes | no | unclear
}
```

## Longitudinal Use (2 fields)

```
longitudinal_use: {
  uses_longitudinal_data:   yes | no | unclear
  longitudinal_tier:        "0" | "1" | "2" | "3"
}
```

### Longitudinal Tier Definitions

**Tier 0 - Cross-sectional**
- Single timepoint inputs
- Static outcome labels
- Example: Baseline MRI → tumor type

**Tier 1 - Longitudinal outcomes only**
- Survival/time-to-event modeled
- Inputs are static (baseline)
- Example: Baseline features → OS prediction

**Tier 2 - Limited longitudinal inputs**
- ≥2 timepoints
- No explicit trajectory modeling
- Example: Pre/post MRI → response

**Tier 3 - True longitudinal**
- Time-series modeling
- Temporal dynamics
- Example: Serial scans → progression trajectory

## Neuro-Oncology Domain (4 fields)

```
neuro_oncology_domain: {
  neuro_onc_domain:        adult_primary_brain_tumors |
                           pediatric_brain_tumors |
                           brain_metastases |
                           mixed_or_unspecified

  primary_vs_metastatic:   primary | metastatic | both | unclear

  compartment:             intra_axial | extra_axial | intraventricular |
                           sellar_suprasellar | cranial_nerve | spinal |
                           leptomeningeal | mixed | unspecified

  who_family:              gliomas_glioneuronal_neuronal | ependymal |
                           choroid_plexus | embryonal | pineal |
                           cranial_paraspinal_nerve | meningiomas |
                           mesenchymal_non_meningothelial | melanocytic |
                           hematolymphoid | germ_cell | sellar_region |
                           metastases_to_cns | mixed | unspecified
}
```

## Total Field Count

- **Basic metadata**: 3
- **Study type**: 1
- **Datasets** (per entry): 3
- **Task & outcomes**: 2
- **Model details**: 2
- **Validation**: 3
- **Longitudinal**: 2
- **Neuro-oncology**: 4

**Total**: 20 top-level fields (datasets can have multiple entries)

## Common Patterns

### Glioblastoma Survival Study
```json
{
  "study_type": "clinical_prediction",
  "task_type": "survival_prediction",
  "outcomes_modeled": "overall_survival",
  "model_class": "deep_learning",
  "modalities_used": ["imaging", "clinical_structured"],
  "longitudinal_tier": "1",
  "neuro_oncology_domain": {
    "neuro_onc_domain": "adult_primary_brain_tumors",
    "primary_vs_metastatic": "primary",
    "compartment": "intra_axial",
    "who_family": "gliomas_glioneuronal_neuronal"
  }
}
```

### Meningioma Segmentation
```json
{
  "study_type": "methodological",
  "task_type": "segmentation",
  "outcomes_modeled": "none_or_not_applicable",
  "model_class": "deep_learning",
  "modalities_used": ["imaging"],
  "longitudinal_tier": "0",
  "neuro_oncology_domain": {
    "neuro_onc_domain": "adult_primary_brain_tumors",
    "primary_vs_metastatic": "primary",
    "compartment": "extra_axial",
    "who_family": "meningiomas"
  }
}
```

### Pediatric Medulloblastoma
```json
{
  "study_type": "clinical_prediction",
  "task_type": "molecular_prediction",
  "outcomes_modeled": "other",
  "model_class": "traditional_ml",
  "modalities_used": ["genomics_or_molecular", "imaging"],
  "longitudinal_tier": "0",
  "neuro_oncology_domain": {
    "neuro_onc_domain": "pediatric_brain_tumors",
    "primary_vs_metastatic": "primary",
    "compartment": "intra_axial",
    "who_family": "embryonal"
  }
}
```

### Brain Metastases Response
```json
{
  "study_type": "clinical_prediction",
  "task_type": "treatment_response",
  "outcomes_modeled": "response",
  "model_class": "deep_learning",
  "modalities_used": ["imaging"],
  "longitudinal_tier": "2",
  "neuro_oncology_domain": {
    "neuro_onc_domain": "brain_metastases",
    "primary_vs_metastatic": "metastatic",
    "compartment": "intra_axial",
    "who_family": "metastases_to_cns"
  }
}
```

## Tips for Extraction

1. **Use "unclear"** when information is not in abstract - don't guess
2. **Be specific** about compartment and WHO family when stated
3. **Longitudinal tier** - focus on what the model actually does, not just data structure
4. **Validation** - only mark "yes" if explicitly stated
5. **Primary dataset** - the main dataset analyzed
6. **Task type** - classification is for non-molecular categorical prediction

## Edge Cases

### Multiple Tumor Types
```json
{
  "neuro_onc_domain": "mixed_or_unspecified",
  "who_family": "mixed"
}
```

### Unclear Compartment
```json
{
  "compartment": "unspecified"
}
```

### Multimodal with Traditional + Deep Learning
```json
{
  "model_class": "hybrid",
  "modalities_used": ["imaging", "genomics_or_molecular", "clinical_structured"]
}
```

### Descriptive Study (No Modeling)
```json
{
  "task_type": "unclear",
  "outcomes_modeled": "none_or_not_applicable",
  "longitudinal_tier": "0"
}
```
