"""
LLM Screening - Prepare Batch with Structured Outputs
Prepares batch requests for inclusion/exclusion screening using Pydantic schemas.
"""

import json
import copy
from tqdm import tqdm
from openai.lib._pydantic import to_strict_json_schema
from schemas import ScreeningDecision
import os

# Resolve project root relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_studies(studies_file):
    """Load studies from JSONL file."""
    studies = []
    with open(studies_file, "r") as f:
        for line in f:
            study = json.loads(line)
            studies.append(study)
    return studies


def load_screening_instructions(instructions_file):
    """Load screening instructions from text file."""
    with open(instructions_file, "r") as f:
        return f.read().strip()


def create_screening_batch(studies, instructions, output_file, 
                          model="gpt-5.2", effort="high"):
    """
    Create batch requests for screening with structured JSON output.
    
    Args:
        studies: List of studies to screen
        instructions: Screening instructions text
        output_file: Where to save batch requests
        model: LLM model to use
        effort: Reasoning effort level (low, medium, high)
    
    Returns:
        List of batch request objects
    """
    # Get strict JSON schema from Pydantic model
    schema = to_strict_json_schema(ScreeningDecision)
    
    # Create request template
    template = {
        "custom_id": "", 
        "method": "POST", 
        "url": "/v1/responses",
        "body": {
            "model": model, 
            "reasoning": {"effort": effort}, 
            "instructions": instructions,
            "input": "",
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "screening_decision",
                    "schema": schema,
                    "strict": True
                }
            }
        }
    }
    
    # Create batch requests
    batch_request = []
    
    for idx, study in enumerate(tqdm(studies, desc="Creating screening batch")):
        query = f"Title: {study['Title']}\nAbstract: {study['Abstract']}"
        request = copy.deepcopy(template)
        request["custom_id"] = str(idx)
        request["body"]["input"] = query
        batch_request.append(request)
    
    # Save to file
    with open(output_file, "w") as f:
        for item in batch_request:
            f.write(json.dumps(item) + "\n")
    
    print(f"Created {len(batch_request)} screening batch requests")
    print(f"Saved to: {output_file}")
    
    return batch_request


def main():
    """Main function to prepare screening batch. Default: full run (all deduped studies)."""
    import argparse
    parser = argparse.ArgumentParser(description="Prepare screening batch requests")
    parser.add_argument(
        "--studies",
        default=os.path.join(BASE_DIR, "preprocessing", "deduped_and_processed_studies.jsonl"),
        help="Input JSONL of studies (default: full deduped list)",
    )
    parser.add_argument("--output", default="screening_batch_requests.jsonl", help="Output batch JSONL")
    args = parser.parse_args()
    studies_file = args.studies if os.path.isabs(args.studies) else os.path.join(BASE_DIR, args.studies)
    output_file = args.output if os.path.isabs(args.output) else os.path.join(BASE_DIR, args.output)
    instructions_file = os.path.join(BASE_DIR, "Prompts", "dataset_screening_instructions.txt")

    print("Loading studies...")
    studies = load_studies(studies_file)
    print(f"Loaded {len(studies)} studies")

    print("\nLoading screening instructions...")
    instructions = load_screening_instructions(instructions_file)

    print("\nCreating batch requests...")
    batch_request = create_screening_batch(
        studies=studies,
        instructions=instructions,
        output_file=output_file,
        model="gpt-5.2",
        effort="high",
    )
    print(f"\n✓ Ready to submit {output_file} to OpenAI Batch API")


if __name__ == "__main__":
    main()
