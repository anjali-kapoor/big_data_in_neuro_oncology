"""
Batch API Quick Reference
Helper script with common batch operations.
"""

from openai import OpenAI
import json
import time


def submit_batch(input_file, description=""):
    """
    Submit a batch job to OpenAI.
    
    Args:
        input_file: Path to JSONL file with batch requests
        description: Optional description for the batch
    
    Returns:
        Batch object with ID and status
    """
    client = OpenAI()
    
    print(f"Uploading {input_file}...")
    batch_input_file = client.files.create(
        file=open(input_file, "rb"),
        purpose="batch"
    )
    
    print(f"Creating batch job...")
    batch = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/responses",
        completion_window="24h",
        metadata={"description": description} if description else None
    )
    
    print(f"\n✓ Batch submitted successfully!")
    print(f"Batch ID: {batch.id}")
    print(f"Status: {batch.status}")
    print(f"\nSave this ID to check status later:")
    print(f"  batch_id = '{batch.id}'")
    print(f"BATCH_ID={batch.id}")  # for scripting
    
    return batch


def check_batch_status(batch_id):
    """
    Check the status of a batch job.
    
    Args:
        batch_id: ID of the batch to check
    
    Returns:
        Batch object with current status
    """
    client = OpenAI()
    
    batch = client.batches.retrieve(batch_id)
    
    print(f"\nBatch ID: {batch.id}")
    print(f"Status: {batch.status}")
    print(f"Created: {batch.created_at}")
    
    if batch.request_counts:
        total = batch.request_counts.total
        completed = batch.request_counts.completed
        failed = batch.request_counts.failed
        
        print(f"\nProgress:")
        print(f"  Total: {total}")
        print(f"  Completed: {completed} ({completed/total*100:.1f}%)")
        print(f"  Failed: {failed}")
        
        if batch.status == "completed":
            print(f"\n✓ Batch completed!")
            print(f"Output file ID: {batch.output_file_id}")
            if failed > 0:
                print(f"Error file ID: {batch.error_file_id}")
    
    return batch


def download_batch_results(batch_id, output_file):
    """
    Download results from a completed batch.
    
    Args:
        batch_id: ID of the completed batch
        output_file: Where to save the results
    
    Returns:
        True if successful, False otherwise
    """
    client = OpenAI()
    
    batch = client.batches.retrieve(batch_id)
    
    if batch.status != "completed":
        print(f"Batch not completed yet. Status: {batch.status}")
        return False
    
    print(f"Downloading results...")
    result = client.files.content(batch.output_file_id).content
    
    with open(output_file, "wb") as f:
        f.write(result)
    
    print(f"✓ Results saved to: {output_file}")
    
    # Also download errors if any
    if batch.request_counts.failed > 0 and batch.error_file_id:
        error_file = output_file.replace(".jsonl", "_errors.jsonl")
        errors = client.files.content(batch.error_file_id).content
        
        with open(error_file, "wb") as f:
            f.write(errors)
        
        print(f"✓ Errors saved to: {error_file}")
    
    return True


def wait_for_batch(batch_id, check_interval=60):
    """
    Wait for a batch to complete, checking periodically.
    
    Args:
        batch_id: ID of the batch to wait for
        check_interval: Seconds between status checks (default: 60)
    """
    client = OpenAI()
    
    print(f"Waiting for batch {batch_id} to complete...")
    print(f"Checking every {check_interval} seconds (Ctrl+C to stop)")
    
    while True:
        batch = client.batches.retrieve(batch_id)
        status = batch.status
        
        if status == "completed":
            print(f"\n✓ Batch completed!")
            return batch
        elif status in ["failed", "expired", "cancelled"]:
            print(f"\n✗ Batch {status}")
            return batch
        
        # Print progress
        if batch.request_counts:
            completed = batch.request_counts.completed
            total = batch.request_counts.total
            pct = (completed / total * 100) if total else 0
            print(f"Progress: {completed}/{total} ({pct:.1f}%)", end="\r")
        
        time.sleep(check_interval)


def cancel_batch(batch_id):
    """
    Cancel a running batch.
    
    Args:
        batch_id: ID of the batch to cancel
    """
    client = OpenAI()
    
    batch = client.batches.cancel(batch_id)
    print(f"Batch {batch_id} cancelled")
    print(f"Status: {batch.status}")
    
    return batch


def list_batches(limit=10):
    """
    List recent batches.
    
    Args:
        limit: Number of batches to show (default: 10)
    """
    client = OpenAI()
    
    batches = client.batches.list(limit=limit)
    
    print(f"\nRecent batches (last {limit}):")
    print("-" * 80)
    
    for batch in batches.data:
        status = batch.status
        created = batch.created_at
        
        if batch.request_counts:
            progress = f"{batch.request_counts.completed}/{batch.request_counts.total}"
        else:
            progress = "N/A"
        
        print(f"ID: {batch.id}")
        print(f"  Status: {status}")
        print(f"  Progress: {progress}")
        print(f"  Created: {created}")
        print()
    
    return batches


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Submit batch:     python batch_api_helpers.py submit <input_file>")
        print("  Check status:     python batch_api_helpers.py status <batch_id>")
        print("  Download results: python batch_api_helpers.py download <batch_id> <output_file>")
        print("  Wait for batch:   python batch_api_helpers.py wait <batch_id>")
        print("  List batches:     python batch_api_helpers.py list")
        print("  Cancel batch:     python batch_api_helpers.py cancel <batch_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "submit":
        if len(sys.argv) < 3:
            print("Error: input_file required")
            sys.exit(1)
        submit_batch(sys.argv[2])
    
    elif command == "status":
        if len(sys.argv) < 3:
            print("Error: batch_id required")
            sys.exit(1)
        check_batch_status(sys.argv[2])
    
    elif command == "download":
        if len(sys.argv) < 4:
            print("Error: batch_id and output_file required")
            sys.exit(1)
        download_batch_results(sys.argv[2], sys.argv[3])
    
    elif command == "wait":
        if len(sys.argv) < 3:
            print("Error: batch_id required")
            sys.exit(1)
        wait_for_batch(sys.argv[2])
    
    elif command == "list":
        list_batches()
    
    elif command == "cancel":
        if len(sys.argv) < 3:
            print("Error: batch_id required")
            sys.exit(1)
        cancel_batch(sys.argv[2])
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
