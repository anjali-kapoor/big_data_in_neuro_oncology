"""
Pydantic Schemas for Screening and Data Extraction
"""

from pydantic import BaseModel, Field, ConfigDict, constr, field_validator
from typing import List, Literal, Optional


# ----------------------------- 
# Screening Schema
# -----------------------------

class ScreeningDecision(BaseModel):
    """Schema for dataset analytics paper screening."""
    model_config = ConfigDict(populate_by_name=True)
    
    analytical_use_of_dataset: Literal["yes", "no", "unclear"] = Field(
        description="Does the study perform cohort-level quantitative analysis using dataset-derived variables?"
    )
    
    # Minimal fields (always recorded)
    title: str = Field(max_length=500)
    year: Optional[str] = Field(None, max_length=10)
    dataset: List[str] = Field(
        default_factory=list,
        description="List of dataset names from the target dataset list mentioned in the study"
    )

    
    # Exclusion reason (only when analytical_use_of_dataset is 'no' or 'unclear')
    exclusion_reason: Optional[Literal[
        "biospecimen_only",
        "wet_lab_only",
        "molecular_profiling_without_cohort_analysis",
        "narrative_or_commentary",
        "descriptive_only",
        "methods_or_dataset_paper",
        "dataset_mentioned_but_not_analyzed",
        "dataset_not_in_target_list",
        "unclear_from_abstract"
    ]] = Field(
        None,
        description="Reason for exclusion. Required when analytical_use_of_dataset is 'no' or 'unclear'"
    )
    
    # Brief reasoning (always helpful, max 300 chars)
    reasoning: str = Field(
        max_length=300,
        description="Brief explanation for the decision"
    )


# ----------------------------- 
# Data Extraction Schemas - Neuro-Oncology
# -----------------------------

# Core constrained types
YesNoUnsure = Literal["yes", "no", "unsure"]


# Dataset usage schema
class DatasetUsed(BaseModel):
    """Information about a dataset used in the study."""
    raw_name: str = Field(
        max_length=200,
        description="Dataset name as mentioned in the paper"
    )
    dataset_used_standardized: Literal[
        "SEER",
        "CBTRUS",
        "TCGA",
        "TARGET",
        "REMBRANDT",
        "GENIE",
        "CancerLinQ",
        "PBTC",
        "Children’s Oncology Group",
        "Children’s Brain Tumor Network",
        "PDX Brain Tumor National Resource",
        "BraTS",
        "BRISC",
        "UCSF-PDGM",
        "NYUMets",
        "GLASS",
        "IvyGAP",
        "Yale-Brain-Mets-Longitudinal Dataset",
        "BrainMetShare",
        "other"
    ] = Field(description="Standardized dataset name from target list (e.g. TCGA, BraTS) or 'other'")

    role: Literal[
        "primary",
        "secondary",
        "unclear"
    ] = Field(
        description="Dataset's role: primary = main dataset for analysis; secondary = validation, comparison, or supplementary"
    )



# Validation level: single field. External implies internal; prospective implies internal; prospective does NOT imply external.
ValidationLevel = Literal[
    "none",                              # No internal, external, or prospective validation
    "internal_only",                     # Internal only (e.g. cross-validation, train-test split)
    "internal_and_external",             # Internal + external (external implies internal)
    "internal_and_prospective",          # Internal + prospective (prospective implies internal; does NOT imply external)
    "internal_and_external_and_prospective",  # All three
    "unclear"                            # Cannot determine from the text
]


# Longitudinal use schema
class LongitudinalUse(BaseModel):
    """Longitudinal tier for time-structured modeling."""
    longitudinal_tier: Literal["0", "1", "2", "3"] = Field(
        description=(
            "0 = cross-sectional; 1 = longitudinal outcomes only (time-to-event), static inputs; "
            "2 = ≥2 timepoints as flattened features, no temporal sequence model; "
            "3 = explicit temporal/sequence modeling (RNN/LSTM, joint longitudinal-survival, etc.)."
        )
    )


# Neuro-oncology domain schema
class NeuroOncologyDomain(BaseModel):
    """Age domain, tumor origin, compartment, and WHO tumor family."""
    neuro_onc_domain: Literal[
        "adult",
        "pediatric",
        "mixed_age",
        "unclear",
    ] = Field(description="Age/population domain: adult ≥18y; pediatric <18y only; mixed_age; unclear")

    primary_vs_metastatic: Literal[
        "primary_cns",
        "metastatic_to_cns",
        "both",
        "unclear",
    ] = Field(description="primary_cns vs metastatic_to_cns vs both; unclear if not specified")

    compartment: Literal[
        "intra_axial",
        "extra_axial",
        "intraventricular",
        "sellar_suprasellar",
        "cranial_nerve",
        "spinal",
        "leptomeningeal",
        "mixed",
        "unclear",
    ] = Field(description="Anatomical compartment; unclear if not specified")

    who_family: Literal[
        "gliomas_glioneuronal_neuronal",
        "ependymal",
        "choroid_plexus",
        "embryonal",
        "pineal",
        "cranial_paraspinal_nerve",
        "meningiomas",
        "mesenchymal_non_meningothelial",
        "melanocytic",
        "hematolymphoid",
        "germ_cell",
        "sellar_region",
        "metastases_to_cns",
        "mixed",
        "unclear",
    ] = Field(description="WHO tumor family classification; unclear if not specified")


# Free-form dataset extraction (any dataset, no predefined list)
class DatasetUsedFreeForm(BaseModel):
    """Dataset used in study - free-form, any dataset name."""
    dataset_name: str = Field(
        max_length=150,
        description="Standardized/canonical name of the dataset (e.g. TCGA, GEO, CGGA, BraTS). Use common abbreviation if known."
    )
    raw_mention: Optional[str] = Field(
        None,
        max_length=200,
        description="Exact phrase as mentioned in the paper (optional)"
    )
    role: Literal["primary", "secondary", "unclear"] = Field(
        description="Dataset's role: primary = main dataset; secondary = validation/comparison; unclear"
    )


class DatasetsFreeFormExtraction(BaseModel):
    """Extract ANY datasets used - no predefined list. For discovering most-used datasets in neuro-oncology."""
    datasets_used: List[DatasetUsedFreeForm] = Field(
        default_factory=list,
        description="List of all datasets used in the study. Empty if none mentioned."
    )


# Domain-only re-extraction (neuro_onc_domain + primary_vs_metastatic only)
class DomainOnlyExtraction(BaseModel):
    """Minimal schema for re-extracting only neuro_onc_domain and primary_vs_metastatic."""
    neuro_onc_domain: Literal[
        "adult",
        "pediatric",
        "mixed_age",
        "unclear"
    ] = Field(description="Primary domain: adult (≥18y), pediatric (<18y), mixed age, or unclear")

    primary_vs_metastatic: Literal[
        "primary_cns",
        "metastatic_to_cns",
        "both",
        "unclear"
    ] = Field(description="Tumor origin: primary CNS, metastatic to CNS, both, or unclear")

    fuzzy_category_reasoning: Optional[str] = Field(
        None,
        max_length=500,
        description="When you select 'unclear' for either field, provide one sentence explaining why. Omit if neither is unclear."
    )


# Main extraction schema
class Extraction(BaseModel):
    """Complete data extraction schema for neuro-oncology dataset analytics papers."""
    model_config = ConfigDict(populate_by_name=True)
    
    # Basic metadata
    title: str = Field(max_length=500)
    year: Optional[str] = Field(None, max_length=10, description="Publication year (if available)")
    journal: Optional[str] = Field(None, max_length=200, description="Journal name (if available)")
    
    # Study characteristics
    study_type: Literal[
        "methodological",
        "clinical_prediction",
        "biomarker_or_translational_analysis",
        "epidemiologic_analysis",
        "benchmark_challenge",
        "clinical_trial_analysis",
        "dataset_description",
        "narrative_review",
        "unclear",
    ] = Field(
        description=(
            "Primary study type: methodological; clinical_prediction; biomarker_or_translational_analysis; "
            "epidemiologic_analysis; benchmark_challenge; clinical_trial_analysis; dataset_description; "
            "narrative_review; unclear if not determined from abstract."
        )
    )
    
    # Datasets used (can be multiple)
    datasets_used: List[DatasetUsed] = Field(
        default_factory=list,
        description="List of datasets used in the study"
    )
    
    # Task and outcomes
    task_type: Literal[
        "segmentation",
        "detection",
        "classification",
        "survival_prediction",
        "molecular_association",
        "progression_or_recurrence",
        "epidemiologic_modeling",
        "treatment_response",
        "molecular_prediction",
        "translational_bioinformatics",
        "unsupervised_subtyping",
        "unclear",
    ] = Field(
        description=(
            "Primary ML/computational task. survival_prediction = predictive model for individual OS/time-to-event "
            "with formal internal validation; distinct from molecular_association (KM/Cox/LASSO without predictive validation). "
            "translational_bioinformatics = omics analysis for biological insight without individual-level predictive model. "
            "unclear if not determined from abstract."
        )
    )
    
    outcomes_modeled: List[Literal[
        "survival",
        "progression_free_survival",
        "incidence_or_prevalence",
        "tumor_characteristic",
        "metastasis",
        "recurrence",
        "response",
        "functional_outcome",
        "quality_of_life",
        "complications",
        "cost_utilization",
        "none_or_not_applicable",
    ]] = Field(
        default_factory=list,
        description=(
            "Multi-select: all outcome categories explicitly modeled. "
            "Select ALL that apply; use none_or_not_applicable when no clinical/patient-level outcome is modeled."
        ),
    )
    
    # Model characteristics
    model_class: Literal[
        "traditional_ml",
        "deep_learning",
        "foundation_model",
        "hybrid",
        "unclear",
    ] = Field(
        description=(
            "Model class. traditional_ml includes Cox, KM, log-rank, nomogram, LASSO/ridge/elastic net, "
            "logistic regression, SVM, RF, GBM—statistical survival without neural networks. "
            "unclear if not determined from abstract."
        )
    )
    
    modalities_used: List[Literal[
        "imaging",
        "pathology",
        "omics",
        "clinical_structured",
        "clinical_text",
        "experimental_preclinical",
        "registry_or_administrative",
        "other"
    ]] = Field(
        default_factory=list,
        description="Data types used: imaging, pathology, omics, clinical_structured, clinical_text, experimental_preclinical, registry_or_administrative, other"
    )
    
    # Validation and longitudinal aspects
    validation_level: ValidationLevel = Field(
        description="Highest level of validation performed. External implies internal; prospective implies internal; prospective does not imply external."
    )
    longitudinal_use: LongitudinalUse
    
    # Neuro-oncology specific
    neuro_oncology_domain: NeuroOncologyDomain

    fuzzy_category_reasoning: Optional[str] = Field(
        None,
        max_length=500,
        description=(
            "When study_type, task_type, outcomes_modeled, model_class, validation_level, longitudinal tier, "
            "neuro-oncology fields, or dataset role is unclear/mixed—or modalities_used includes other—"
            "provide one sentence explaining why. Omit if no such category was selected."
        ),
    )
