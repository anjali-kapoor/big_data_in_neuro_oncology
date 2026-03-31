"""
CSV to JSONL Converter
Converts deduplicated CSV from ris_import_deduplicate.py to JSONL format
for use with screening scripts. Run from project root.
"""

import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def csv_to_jsonl(input_csv, output_jsonl):
    """
    Convert CSV to JSONL format.
    
    Args:
        input_csv: Path to deduplicated CSV file
        output_jsonl: Path for output JSONL file
    """
    # Read CSV
    print(f"Reading {input_csv}...")
    df = pd.read_csv(input_csv)
    
    print(f"Loaded {len(df)} studies")
    print(f"Columns: {list(df.columns)}")
    
    # Check for required columns
    required_cols = ['title', 'abstract']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Standardize column names to match expected format
    # Expected: Title, Abstract, Year, DOI, Authors
    column_mapping = {
        'title': 'Title',
        'abstract': 'Abstract',
        'year': 'Year',
        'doi': 'DOI',
        'authors': 'Authors'
    }
    
    # Rename columns
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Handle missing abstracts
    initial_count = len(df)
    df = df.dropna(subset=['Title', 'Abstract'])
    dropped = initial_count - len(df)
    if dropped > 0:
        print(f"Warning: Dropped {dropped} studies without title or abstract")
    
    # Convert to JSONL
    print(f"\nWriting {len(df)} studies to {output_jsonl}...")
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for _, row in df.iterrows():
            # Create study object
            study = {
                'Title': str(row['Title']),
                'Abstract': str(row['Abstract'])
            }
            
            # Add optional fields if present
            if 'Year' in row and pd.notna(row['Year']):
                study['Year'] = str(int(row['Year'])) if isinstance(row['Year'], float) else str(row['Year'])
            
            if 'DOI' in row and pd.notna(row['DOI']):
                study['DOI'] = str(row['DOI'])
            
            if 'Authors' in row and pd.notna(row['Authors']):
                study['Authors'] = str(row['Authors'])
            
            # Write as JSON line
            f.write(json.dumps(study, ensure_ascii=False) + '\n')
    
    print(f"✓ Successfully converted {len(df)} studies")
    print(f"✓ Output: {output_jsonl}")
    
    # Print sample
    print("\nSample study:")
    sample = df.iloc[0]
    print(f"  Title: {sample['Title'][:80]}...")
    print(f"  Abstract: {sample['Abstract'][:100]}...")
    if 'Year' in sample and pd.notna(sample['Year']):
        print(f"  Year: {sample['Year']}")


def main():
    """Main function to convert CSV to JSONL. Run from project root."""
    input_csv = BASE_DIR / "preprocessing" / "all_references_without_duplicates.csv"
    output_jsonl = BASE_DIR / "preprocessing" / "deduped_and_processed_studies.jsonl"
    csv_to_jsonl(str(input_csv), str(output_jsonl))
    print("\n" + "="*60)
    print("Next steps (full run):")
    print("="*60)
    print("  python main_workflow/screening_1_prepare_batch.py")
    print("  python main_workflow/batch_api_helpers.py submit screening_batch_requests.jsonl")
    print("  python main_workflow/batch_api_helpers.py wait <batch_id>")
    print("  python main_workflow/batch_api_helpers.py download <batch_id> \"Batch Responses/screening_output.jsonl\"")
    print("  python main_workflow/screening_2_process_results.py")
    print("="*60)


if __name__ == "__main__":
    main()
