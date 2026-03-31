"""
Data Extraction - Prepare Batch with Structured Outputs
Prepares batch requests for extracting structured data from included studies.
"""

import json
import copy
from tqdm import tqdm
from openai.lib._pydantic import to_strict_json_schema
from schemas import Extraction
from pathlib import Path


def load_included_studies(studies_file):
    """Load included studies from JSONL file."""
    studies = []
    with open(studies_file, "r") as f:
        for line in f:
            study = json.loads(line)
            studies.append(study)
    return studies


def load_extraction_instructions(instructions_file):
    """Load extraction instructions from text file."""
    with open(instructions_file, "r") as f:
        return f.read().strip()


def create_extraction_batch(studies, instructions, output_file, model="gpt-5.2", effort="high"):
    """
    Create batch requests for data extraction with structured JSON output.
    
    Args:
        studies: List of included studies
        instructions: Extraction instructions text
        output_file: Where to save batch requests
        model: LLM model to use
        effort: Reasoning effort level
    
    Returns:
        List of batch request objects
    """
    
    # Get strict JSON schema from Pydantic model
    schema = to_strict_json_schema(Extraction)
    
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
                    "name": "study_extraction",
                    "schema": schema,
                    "strict": True
                }
            }
        }
    }
    
    # Create batch requests
    batch_request = []
    
    for idx, study in enumerate(tqdm(studies, desc="Creating extraction batch")):
        year = study.get('Year') or (study.get('screening_decision') or {}).get('year') or ''
        query = f"Title: {study.get('Title','')}\nYear: {year}\nAbstract: {study.get('Abstract','')}"
        request = copy.deepcopy(template)
        request["custom_id"] = str(idx)
        request["body"]["input"] = query
        batch_request.append(request)
    
    # Save to file
    with open(output_file, "w") as f:
        for item in batch_request:
            f.write(json.dumps(item) + "\n")
    
    print(f"Created {len(batch_request)} extraction batch requests")
    print(f"Saved to: {output_file}")
    
    return batch_request


def main():
    """Main function to prepare extraction batch."""
    import argparse
    parser = argparse.ArgumentParser(description="Prepare extraction batch requests")
    parser.add_argument("--studies", default="included_studies.jsonl", help="Input JSONL of studies (default: included_studies.jsonl)")
    parser.add_argument("--instructions", default="Prompts/extraction_instructions.txt", help="Path to extraction instructions")
    parser.add_argument("--output", default="data_extraction_batch_requests.jsonl", help="Output batch requests JSONL")
    args = parser.parse_args()

    # Paths relative to project root (parent of main_workflow)
    base = Path(__file__).resolve().parent.parent
    studies_path = base / args.studies if not Path(args.studies).is_absolute() else Path(args.studies)
    instructions_path = base / args.instructions if not Path(args.instructions).is_absolute() else Path(args.instructions)
    output_path = base / args.output if not Path(args.output).is_absolute() else Path(args.output)

    print("Loading studies...")
    studies = load_included_studies(studies_path)
    print(f"Loaded {len(studies)} studies")

    print("\nLoading extraction instructions...")
    instructions = load_extraction_instructions(instructions_path)

    print("\nCreating extraction batch requests...")
    create_extraction_batch(
        studies=studies,
        instructions=instructions,
        output_file=output_path,
        model="gpt-5.2",
        effort="high"
    )

    print(f"\n✓ Ready to submit {output_path} to OpenAI Batch API")


if __name__ == "__main__":
    main()
