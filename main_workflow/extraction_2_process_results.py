"""
Data Extraction - Process Batch Results
Processes extraction batch results and handles failures.
"""

import json
from tqdm import tqdm
from openai import OpenAI
from collections import defaultdict


def load_included_studies(studies_file):
    """Load included studies from JSONL file."""
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


def _get_extraction_text_from_output(output_list):
    """
    Get the extraction text from API output list.
    Some responses have output[0]=reasoning, output[1]=message; others have only output[0]=message.
    """
    if not output_list:
        return None
    for block in output_list:
        content = block.get("content") or []
        if content and isinstance(content[0].get("text"), str):
            return content[0]["text"]
    return None


def process_extraction_responses(studies, responses):
    """
    Process batch responses and add extracted data to studies.
    
    Args:
        studies: Original list of studies
        responses: Batch API responses
    
    Returns:
        Tuple of (updated_studies, failures)
    """
    failures = []
    
    # Sort responses by custom_id to match study order
    responses_dict = {int(r["custom_id"]): r for r in responses}
    
    for idx, study in enumerate(tqdm(studies, desc="Processing extraction responses")):
        try:
            if idx not in responses_dict:
                failures.append((idx, "Missing response", None))
                continue
            
            response = responses_dict[idx]
            output_list = response.get("response", {}).get("body", {}).get("output") or []
            extracted_data = _get_extraction_text_from_output(output_list)
            if extracted_data is None:
                failures.append((idx, "No text in output", response))
                continue
            
            # Parse extracted data (should already be valid JSON)
            if isinstance(extracted_data, str):
                extracted_data = json.loads(extracted_data)
            
            # Backfill year from source when extraction left it empty (we have Year in study data)
            if not extracted_data.get("year"):
                source_year = study.get("Year") or (study.get("screening_decision") or {}).get("year")
                if source_year:
                    extracted_data["year"] = str(source_year) if source_year else None
            
            # Add extracted data to study
            study["extracted_data"] = extracted_data
            
        except Exception as e:
            failures.append((idx, str(e), response if idx in responses_dict else None))
            continue
    
    print(f"\nSuccessfully processed: {len(studies) - len(failures)}")
    print(f"Failures: {len(failures)}")
    
    return studies, failures


def retry_failed_extractions(failures, studies, instructions_file, client=None):
    """
    Retry failed extraction requests using synchronous API calls.
    
    Args:
        failures: List of (index, error, response) tuples
        studies: List of studies to update
        instructions_file: Path to extraction instructions
        client: OpenAI client (creates new if None)
    
    Returns:
        Updated studies
    """
    if client is None:
        client = OpenAI()
    
    from openai.lib._pydantic import to_strict_json_schema
    from schemas import Extraction
    
    schema = to_strict_json_schema(Extraction)
    
    # Load instructions
    with open(instructions_file, "r") as f:
        instructions = f.read().strip()
    
    print(f"\nRetrying {len(failures)} failed extractions...")
    
    for idx, error, _ in tqdm(failures, desc="Retrying"):
        try:
            if idx >= len(studies):
                print(f"Index {idx} out of range, skipping")
                continue
            
            study = studies[idx]
            year = study.get("Year") or (study.get("screening_decision") or {}).get("year") or ""
            query = f"Title: {study.get('Title','')}\nYear: {year}\nAbstract: {study.get('Abstract', '')}"
            
            result = client.responses.create(
                model="gpt-5.2",
                instructions=instructions,
                input=query,
                reasoning={"effort": "high"},
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "study_extraction",
                        "schema": schema,
                        "strict": True
                    }
                }
            )
            
            # Extract data (message block may be output[0] or output[1] depending on API)
            message_block = next(
                (o for o in result.output if getattr(o, "content", None)),
                None
            )
            if not message_block or not message_block.content:
                print(f"No content in response for index {idx}, skipping")
                continue
            extracted_data = message_block.content[0].text
            if isinstance(extracted_data, str):
                extracted_data = json.loads(extracted_data)
            
            # Update study
            studies[idx]["extracted_data"] = extracted_data
            
        except Exception as e:
            print(f"Failed again for index {idx}: {str(e)}")
            continue
    
    return studies


def save_studies_with_extractions(studies, output_file):
    """Save studies with extracted data to JSONL file."""
    with open(output_file, "w") as f:
        for study in studies:
            f.write(json.dumps(study) + "\n")
    print(f"\nSaved {len(studies)} studies with extracted data to {output_file}")


def analyze_extracted_fields(studies):
    """
    Analyze extracted fields to show coverage and unique values.
    
    Args:
        studies: List of studies with extracted_data
    """
    field_stats = defaultdict(lambda: {"count": 0, "unique_values": set()})
    total_studies = len(studies)
    
    for study in studies:
        if "extracted_data" not in study:
            continue
        
        for field, value in study["extracted_data"].items():
            if value is None:
                continue
            
            field_stats[field]["count"] += 1
            
            if isinstance(value, list):
                for item in value:
                    if item and item != "unsure":
                        field_stats[field]["unique_values"].add(str(item))
            elif isinstance(value, dict):
                # For nested objects, just count presence
                pass
            elif value != "unsure":
                field_stats[field]["unique_values"].add(str(value))
    
    print("\n" + "="*80)
    print("EXTRACTED FIELDS ANALYSIS")
    print("="*80)
    print(f"Total studies: {total_studies}")
    print(f"\n{'Field':<40} {'Coverage':<15} {'Unique Values':<15}")
    print("-"*80)
    
    for field in sorted(field_stats.keys()):
        count = field_stats[field]["count"]
        unique = len(field_stats[field]["unique_values"])
        coverage_pct = (count / total_studies * 100) if total_studies > 0 else 0
        
        print(f"{field:<40} {count:>5}/{total_studies} ({coverage_pct:>5.1f}%) {unique:>10}")
    
    print("="*80)
    
    return field_stats


def export_field_values(studies, field_name, output_file=None):
    """
    Export all unique values for a specific field.
    
    Args:
        studies: List of studies with extracted_data
        field_name: Name of the field to export
        output_file: Optional file to save values
    
    Returns:
        Set of unique values
    """
    values = set()
    
    for study in studies:
        if "extracted_data" not in study:
            continue
        
        field_data = study["extracted_data"].get(field_name)
        
        if isinstance(field_data, list):
            for item in field_data:
                if item and item != "unsure":
                    values.add(str(item))
        elif field_data and field_data != "unsure":
            values.add(str(field_data))
    
    if output_file:
        with open(output_file, "w") as f:
            for value in sorted(values):
                f.write(value + "\n")
        print(f"Exported {len(values)} unique values for '{field_name}' to {output_file}")
    
    return values


def main():
    """Main function to process extraction results."""
    import argparse
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Process extraction batch responses")
    parser.add_argument("--studies", default="included_studies.jsonl", help="Input studies JSONL")
    parser.add_argument("--responses", default="Batch Responses/data_extraction_output.jsonl", help="Batch responses JSONL")
    parser.add_argument("--output", default="studies_with_extracted_data.jsonl", help="Output JSONL")
    args = parser.parse_args()
    included_studies_file = root / args.studies if not Path(args.studies).is_absolute() else Path(args.studies)
    responses_file = root / args.responses if not Path(args.responses).is_absolute() else Path(args.responses)
    output_file = root / args.output if not Path(args.output).is_absolute() else Path(args.output)
    instructions_file = root / "Prompts/extraction_instructions.txt"

    # Load data
    print("Loading included studies...")
    studies = load_included_studies(included_studies_file)
    print(f"Loaded {len(studies)} included studies")
    
    print("\nLoading batch responses...")
    responses = load_batch_responses(responses_file)
    print(f"Loaded {len(responses)} responses")
    
    # Process responses
    print("\nProcessing responses...")
    studies, failures = process_extraction_responses(studies, responses)
    
    # Retry failures if any
    if failures:
        print(f"\nFound {len(failures)} failures")
        retry_choice = input("Retry failures? (y/n): ").lower()
        
        if retry_choice == 'y':
            studies = retry_failed_extractions(failures, studies, instructions_file)

    # Save results
    print("\nSaving results...")
    save_studies_with_extractions(studies, output_file)
    
    # Analyze extracted fields
    field_stats = analyze_extracted_fields(studies)
    
    # Optional: Export specific field values
    export_choice = input("\nExport specific field values? (y/n): ").lower()
    if export_choice == 'y':
        field_name = input("Enter field name: ")
        export_file = f"{field_name}_values.txt"
        export_field_values(studies, field_name, export_file)
    
    print(f"\n✓ Processing complete!")
    print(f"✓ Studies with extracted data: {output_file}")


if __name__ == "__main__":
    main()
