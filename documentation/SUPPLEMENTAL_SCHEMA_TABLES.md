# Supplemental Materials: Screening and Extraction Schema Definitions

---

## Screening schema definitions

| Field | Type | Description | Values / Options |
|-------|------|-------------|------------------|
| **analytical_use_of_dataset** | Literal | Does the study perform cohort-level quantitative analysis using dataset-derived variables? | `yes`, `no`, `unclear` |
| **title** | string | Paper title | Max 500 characters |
| **year** | string | Publication year | Max 10 characters; null if unavailable |
| **dataset** | list | Dataset names from the target dataset list mentioned in the study | List of strings; empty list if none |
| **exclusion_reason** | Literal | Reason for exclusion. Required when analytical_use_of_dataset is `no` or `unclear` | See exclusion categories below |
| **reasoning** | string | Brief explanation for the decision | Max 300 characters |

### Exclusion Reason Categories

| Code | Description |
|------|-------------|
| `biospecimen_only` | Dataset used only as a source of biological specimens (tissue, cell lines, organoids, PDX models) without cohort-level analysis of dataset variables |
| `wet_lab_only` | Primarily laboratory or preclinical experiments where dataset mention is incidental and not analyzed computationally |
| `molecular_profiling_without_cohort_analysis` | Molecular profiling, genomic analysis, or laboratory assays on samples from a dataset without cohort-level statistical or computational analysis |
| `narrative_or_commentary` | Narrative review, editorial, perspective, commentary, or survey without original dataset analysis |
| `descriptive_only` | Dataset used only to describe a small number of cases without statistical or computational analysis |
| `methods_or_dataset_paper` | Dataset creation, curation, annotation, or challenge overview paper without downstream cohort-level analysis |
| `dataset_mentioned_but_not_analyzed` | Dataset is cited or mentioned but not directly analyzed to produce study results |
| `dataset_not_in_target_list` | Study analyzes datasets that are not included in the provided target dataset list |
| `unclear_from_abstract` | The abstract does not provide sufficient information to determine dataset usage or analysis type |

---

## Data extraction schema definitions

### Basic Metadata and Study Characteristics

| Field | Type | Description | Values / Options |
|-------|------|-------------|------------------|
| **title** | string | Full paper title | Max 500 characters |
| **year** | string | Publication year | Max 10 characters; null if unavailable |
| **journal** | string | Journal name | Max 200 characters; null if unavailable |
| **study_type** | Literal | Primary study type | `methodological`, `clinical_prediction`, `biomarker_or_translational_analysis`, `epidemiologic_analysis`, `benchmark_challenge`, `clinical_trial_analysis`, `dataset_description`, `narrative_review`, `other` |

### Datasets Used

| Field | Type | Description | Values / Options |
|-------|------|-------------|------------------|
| **datasets_used** | list | List of datasets used in the study | Array of DatasetUsed objects (see below) |

**DatasetUsed object:**

| Sub-field | Type | Description | Values / Options |
|-----------|------|-------------|------------------|
| `raw_name` | string | Dataset name as mentioned in the paper | Max 200 characters |
| `dataset_used_standardized` | Literal | Standardized dataset name from target list | SEER, CBTRUS, TCGA, TARGET, REMBRANDT, GENIE, CancerLinQ, PBTC, Children's Oncology Group, Children's Brain Tumor Network, PDX Brain Tumor National Resource, BraTS, BRISC, UCSF-PDGM, NYUMets, GLASS, IvyGAP, Yale-Brain-Mets-Longitudinal Dataset, BrainMetShare, `other` |
| `role` | Literal | Dataset's role in the study | `primary` (main dataset for analysis), `secondary` (validation, comparison, or supplementary), `unclear` |

### Task and Outcomes

| Field | Type | Description | Values / Options |
|-------|------|-------------|------------------|
| **task_type** | Literal | Primary ML/computational task | `segmentation`, `detection`, `classification`, `survival_prediction`, `molecular_association`, `progression_or_recurrence`, `epidemiologic_modeling`, `treatment_response`, `molecular_prediction`, `translational_bioinformatics`, `unsupervised_subtyping`, `other` |
| **outcomes_modeled** | list | All outcome categories explicitly modeled in the study (select all that apply) | `survival`, `progression_free_survival`, `incidence_or_prevalence`, `tumor_characteristic`, `metastasis`, `recurrence`, `response`, `functional_outcome`, `quality_of_life`, `complications`, `cost_utilization`, `none_or_not_applicable`, `other` |

### Model Characteristics

| Field | Type | Description | Values / Options |
|-------|------|-------------|------------------|
| **model_class** | Literal | Class of model | `traditional_ml` (Cox, Kaplan–Meier, LASSO, SVM, random forest, etc.), `deep_learning` (neural networks, CNNs, transformers), `foundation_model` (pre-trained, e.g., SAM, CLIP), `hybrid`, `unclear` |
| **modalities_used** | list | Data types used (select all that apply) | `imaging`, `pathology`, `omics`, `clinical_structured`, `clinical_text`, `experimental_preclinical`, `registry_or_administrative`, `other` |

### Validation and Longitudinal Use

| Field | Type | Description | Values / Options |
|-------|------|-------------|------------------|
| **validation_level** | Literal | Highest level of validation performed. External implies internal; prospective implies internal | `none`, `internal_only`, `internal_and_external`, `internal_and_prospective`, `internal_and_external_and_prospective`, `unclear` |
| **longitudinal_use** | object | Longitudinal data usage | See longitudinal_tier below |

**longitudinal_tier:**

| Tier | Description |
|------|-------------|
| `0` | Cross-sectional (single timepoint) |
| `1` | Longitudinal outcomes only (survival), static inputs |
| `2` | Limited longitudinal inputs (2+ timepoints, no trajectory modeling) |
| `3` | True longitudinal modeling (time-series, temporal dynamics) |

### Neuro-Oncology Domain (newer version)

| Field | Type | Description | Values / Options |
|-------|------|-------------|------------------|
| **neuro_onc_domain** | Literal | Primary age domain | `adult` (≥18y), `pediatric` (<18y), `mixed_age`, `unclear` |
| **primary_vs_metastatic** | Literal | Tumor origin | `primary_cns`, `metastatic_to_cns`, `both`, `unclear` |
| **compartment** | Literal | Anatomical compartment | `intra_axial`, `extra_axial`, `intraventricular`, `sellar_suprasellar`, `cranial_nerve`, `spinal`, `leptomeningeal`, `mixed`, `unclear` |
| **who_family** | Literal | WHO tumor family classification | `gliomas_glioneuronal_neuronal`, `ependymal`, `choroid_plexus`, `embryonal`, `pineal`, `cranial_paraspinal_nerve`, `meningiomas`, `mesenchymal_non_meningothelial`, `melanocytic`, `hematolymphoid`, `germ_cell`, `sellar_region`, `metastases_to_cns`, `mixed`, `unclear` |

### Supplemental Field

| Field | Type | Description |
|-------|------|-------------|
| **fuzzy_category_reasoning** | string | When selecting `other`, `unclear`, or `mixed` for any field above, one-sentence explanation (for debugging). Omit if none selected. | Max 500 characters |

---

*Schema source: `main_workflow/schemas.py`. Domain and outcome definitions use the current (newer) versions.*
