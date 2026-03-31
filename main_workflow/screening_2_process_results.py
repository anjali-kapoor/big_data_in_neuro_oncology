"""
LLM Screening - Process Batch Results
Processes screening batch results and handles failures.
"""

import json
from tqdm import tqdm
from openai import OpenAI
from typing import List, Tuple, Dict


def load_studies(studies_file):
    """Load original studies from JSONL file."""
    studies = []
    with open(studies_file, "r") as f:
        for line in f:
            study = json.loads(line)
            studies.append(study)
    return studies


def load_batch_responses(responses_file):
    """Load batch API responses from JSONL file."""
    responses = []
    with open(responses_file, "r") as f:
        for line in f:
            response = json.loads(line)
            responses.append(response)
    return responses


def process_screening_responses(studies, responses):
    """
    Process batch responses and add screening decisions to studies.
    
    Args:
        studies: Original list of studies
        responses: Batch API responses
    
    Returns:
        Tuple of (updated_studies, failures)
    """
    failures = []
    
    # Sort responses by custom_id to match study order
    responses_dict = {int(r["custom_id"]): r for r in responses}
    
    for idx, study in enumerate(tqdm(studies, desc="Processing screening responses")):
        try:
            if idx not in responses_dict:
                failures.append((idx, "Missing response", None))
                continue
            
            response = responses_dict[idx]
            
            # Extract the structured JSON response
            # With structured outputs, the response should already be valid JSON
            outputs = response["response"]["body"]["output"]

            message_block = next(
                o for o in outputs if o["type"] == "message"
            )

            decision = message_block["content"][0]["text"]

            
            # Parse decision (should already be valid JSON)
            if isinstance(decision, str):
                decision_data = json.loads(decision)
            else:
                decision_data = decision
            
            # Add screening decision to study
            study["screening_decision"] = decision_data
            study["analytical_use_of_dataset"] = decision_data["analytical_use_of_dataset"]
            study["dataset"] = decision_data.get("dataset", [])
            study["year"] = decision_data.get("year", None)
            study["reasoning"] = decision_data.get("reasoning", "")
            
            # Add exclusion reason if present
            if decision_data.get("exclusion_reason"):
                study["exclusion_reason"] = decision_data["exclusion_reason"]
            
        except Exception as e:
            failures.append((idx, str(e), response if idx in responses_dict else None))
            continue
    
    print(f"\nSuccessfully processed: {len(studies) - len(failures)}")
    print(f"Failures: {len(failures)}")
    
    return studies, failures


def retry_failed_screenings(failures, studies, instructions, client=None):
    """
    Retry failed screening requests using synchronous API calls.
    
    Args:
        failures: List of (index, error, response) tuples
        studies: List of studies to update
        instructions: Screening instructions
        client: OpenAI client (creates new if None)
    
    Returns:
        Updated studies
    """
    if client is None:
        client = OpenAI()
    
    from openai.lib._pydantic import to_strict_json_schema
    from schemas import ScreeningDecision
    
    schema = to_strict_json_schema(ScreeningDecision)
    
    print(f"\nRetrying {len(failures)} failed screenings...")
    
    for idx, error, _ in tqdm(failures, desc="Retrying"):
        try:
            if idx >= len(studies):
                print(f"Index {idx} out of range, skipping")
                continue
            
            study = studies[idx]
            query = f"Title: {study['Title']}\nAbstract: {study.get('Abstract', '')}"
            
            result = client.responses.create(
                model="gpt-5.2",
                instructions=instructions,
                input=query,
                reasoning={"effort": "high"},
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "screening_decision",
                        "schema": schema,
                        "strict": True
                    }
                }
            )
            
            # Extract decision
            message_block = next(
                o for o in result.output
                if o.type == "message"
            )

            decision = message_block.content[0].text

            if isinstance(decision, str):
                decision_data = json.loads(decision)
            else:
                decision_data = decision
            
            # Update study
            studies[idx]["screening_decision"] = decision_data
            studies[idx]["analytical_use_of_dataset"] = decision_data["analytical_use_of_dataset"]
            studies[idx]["dataset"] = decision_data.get("dataset", [])
            studies[idx]["year"] = decision_data.get("year", None)
            studies[idx]["reasoning"] = decision_data.get("reasoning", "")
            
            if decision_data.get("exclusion_reason"):
                studies[idx]["exclusion_reason"] = decision_data["exclusion_reason"]
            
        except Exception as e:
            print(f"Failed again for index {idx}: {str(e)}")
            continue
    
    return studies


def save_screened_studies(studies, output_file):
    """Save studies with screening decisions to JSONL file."""
    with open(output_file, "w") as f:
        for study in studies:
            f.write(json.dumps(study) + "\n")
    print(f"\nSaved {len(studies)} studies to {output_file}")


def get_screening_statistics(studies):
    """Calculate and print screening statistics."""
    total = len(studies)
    analytical_yes = sum(1 for s in studies if s.get("analytical_use_of_dataset") == "yes")
    analytical_no = sum(1 for s in studies if s.get("analytical_use_of_dataset") == "no")
    analytical_unclear = sum(1 for s in studies if s.get("analytical_use_of_dataset") == "unclear")
    no_decision = total - analytical_yes - analytical_no - analytical_unclear
    
    # Count exclusion reasons
    exclusion_reasons = {}
    for s in studies:
        if s.get("exclusion_reason"):
            reason = s["exclusion_reason"]
            exclusion_reasons[reason] = exclusion_reasons.get(reason, 0) + 1
    
    print("\n" + "="*70)
    print("SCREENING STATISTICS")
    print("="*70)
    print(f"Total studies screened: {total}")
    print(f"\nAnalytical use of dataset:")
    print(f"  YES (included):  {analytical_yes:>5} ({analytical_yes/total*100:>5.1f}%)")
    print(f"  NO (excluded):   {analytical_no:>5} ({analytical_no/total*100:>5.1f}%)")
    print(f"  UNCLEAR:         {analytical_unclear:>5} ({analytical_unclear/total*100:>5.1f}%)")
    if no_decision > 0:
        print(f"  No decision:     {no_decision:>5} ({no_decision/total*100:>5.1f}%)")
    
    if exclusion_reasons:
        print(f"\nExclusion reasons breakdown:")
        for reason, count in sorted(exclusion_reasons.items(), key=lambda x: -x[1]):
            print(f"  {reason:<30} {count:>5} ({count/total*100:>5.1f}%)")
    
    print("="*70)
    
    return {
        "total": total,
        "analytical_yes": analytical_yes,
        "analytical_no": analytical_no,
        "analytical_unclear": analytical_unclear,
        "no_decision": no_decision,
        "exclusion_reasons": exclusion_reasons
    }


def filter_included_studies(studies, output_file=None):
    """
    Filter to only studies with analytical use of dataset (yes).
    
    Args:
        studies: All studies with screening decisions
        output_file: Optional file to save included studies
    
    Returns:
        List of included studies
    """
    included = [s for s in studies if s.get("analytical_use_of_dataset") == "yes"]
    
    if output_file:
        with open(output_file, "w") as f:
            for study in included:
                f.write(json.dumps(study) + "\n")
        print(f"\nSaved {len(included)} included studies to {output_file}")
    
    return included


def save_minimal_excluded_studies(studies, output_file="excluded_studies_minimal.jsonl"):
    """
    Save minimal data for excluded/unclear studies.
    
    Args:
        studies: All studies with screening decisions
        output_file: Where to save minimal excluded study data
    """
    excluded = [s for s in studies if s.get("analytical_use_of_dataset") in ["no", "unclear"]]
    
    minimal_data = []
    for study in excluded:
        minimal = {
            "title": study.get("screening_decision", {}).get("title", study.get("Title", "")),
            "year": study.get("year", ""),
            "dataset": study.get("dataset", ""),
            "analytical_use_of_dataset": study.get("analytical_use_of_dataset", ""),
            "exclusion_reason": study.get("exclusion_reason", "")
        }
        minimal_data.append(minimal)
    
    with open(output_file, "w") as f:
        for item in minimal_data:
            f.write(json.dumps(item) + "\n")
    
    print(f"\nSaved {len(minimal_data)} excluded studies (minimal data) to {output_file}")
    return minimal_data


def main():
    """Main function to process screening results. Default: full run (same studies file as screening_1)."""
    import argparse
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Process screening batch results")
    parser.add_argument("--studies", default="preprocessing/deduped_and_processed_studies.jsonl", help="Input studies JSONL")
    parser.add_argument("--responses", default="Batch Responses/screening_output.jsonl", help="Batch responses JSONL")
    parser.add_argument("--output", default="screened_studies.jsonl", help="Output screened studies JSONL")
    parser.add_argument("--included", default="included_studies.jsonl", help="Output included studies JSONL")
    parser.add_argument("--excluded", default="excluded_studies_minimal.jsonl", help="Output excluded minimal JSONL")
    args = parser.parse_args()
    studies_file = root / args.studies if not Path(args.studies).is_absolute() else Path(args.studies)
    responses_file = root / args.responses if not Path(args.responses).is_absolute() else Path(args.responses)
    output_file = root / args.output if not Path(args.output).is_absolute() else Path(args.output)
    included_output_file = root / args.included if not Path(args.included).is_absolute() else Path(args.included)
    excluded_output_file = root / args.excluded if not Path(args.excluded).is_absolute() else Path(args.excluded)
    instructions_file = root / "Prompts/dataset_screening_instructions.txt"

    # Load data
    print("Loading original studies...")
    studies = load_studies(str(studies_file))
    print(f"Loaded {len(studies)} studies")
    
    print("\nLoading batch responses...")
    responses = load_batch_responses(str(responses_file))
    print(f"Loaded {len(responses)} responses")
    
    # Process responses
    print("\nProcessing responses...")
    studies, failures = process_screening_responses(studies, responses)
    
    # Retry failures if any
    if failures:
        print(f"\nFound {len(failures)} failures")
        retry_choice = input("Retry failures? (y/n): ").lower()
        
        if retry_choice == 'y':
            with open(str(instructions_file), "r") as f:
                instructions = f.read().strip()
            
            studies = retry_failed_screenings(failures, studies, instructions)
    
    # Save results
    print("\nSaving results...")
    save_screened_studies(studies, str(output_file))
    
    # Print statistics
    stats = get_screening_statistics(studies)
    
    # Filter and save included studies (analytical_use_of_dataset = "yes")
    included = filter_included_studies(studies, str(included_output_file))

    # Save minimal data for excluded/unclear studies
    save_minimal_excluded_studies(studies, str(excluded_output_file))

    print(f"\n✓ Processing complete!")
    print(f"✓ All screened studies: {output_file}")
    print(f"✓ Included studies (for extraction): {included_output_file}")
    print(f"✓ Excluded studies (minimal data): {excluded_output_file}")


if __name__ == "__main__":
    main()
