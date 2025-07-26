"""
Monitor the corpus processing and report when complete
"""
import json
import time
import os
from pathlib import Path
from document_processor import DocumentProcessor
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def check_processing_status():
    """Check the current status of corpus processing"""
    # Load environment variables
    load_dotenv()
    
    # Check if results file exists
    results_file = "tbi_corpus_processing_results.json"
    if not os.path.exists(results_file):
        return None, "No processing results file found"
    
    # Load results
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Get corpus statistics
    corpus_dir = Path(r"C:\Users\jdall\lexicon-mvp-alpha\tbi-corpus")
    total_files = len(list(corpus_dir.rglob("*.pdf"))) + \
                  len(list(corpus_dir.rglob("*.docx"))) + \
                  len(list(corpus_dir.rglob("*.txt"))) + \
                  len(list(corpus_dir.rglob("*.md")))
    
    processed_count = len(results.get("processed_files", []))
    error_count = len(results.get("errors", []))
    
    # Get collection count
    try:
        processor = DocumentProcessor(collection_name="lexicon_tbi_corpus")
        vector_count = processor.collection.count()
    except:
        vector_count = "Unknown"
    
    status = {
        "total_files": total_files,
        "processed": processed_count,
        "errors": error_count,
        "remaining": total_files - processed_count,
        "vectors": vector_count,
        "complete": processed_count >= (total_files - error_count)
    }
    
    return status, results

def print_summary(status, results):
    """Print a detailed summary of the processing"""
    print("\n" + "="*60)
    print("LEXICON TBI CORPUS PROCESSING SUMMARY")
    print("="*60)
    print(f"Total Files: {status['total_files']}")
    print(f"Processed: {status['processed']}")
    print(f"Errors: {status['errors']}")
    print(f"Remaining: {status['remaining']}")
    print(f"Total Vectors: {status['vectors']}")
    print(f"Status: {'COMPLETE' if status['complete'] else 'IN PROGRESS'}")
    
    if status['errors'] > 0:
        print(f"\n⚠️  {status['errors']} files had errors:")
        for i, error in enumerate(results.get("errors", [])[:5], 1):
            filename = Path(error['file']).name
            print(f"  {i}. {filename}: {error['error'][:50]}...")
    
    if status['complete']:
        print("\n✅ Processing is COMPLETE!")
        print("\nKey Statistics:")
        print(f"  - Successfully processed: {status['processed'] - status['errors']} files")
        print(f"  - Created {status['vectors']} searchable vectors")
        print(f"  - Extracted metadata for {len(results.get('extracted_variables', {}))} documents")
        
        # Sample of extracted experts
        experts = set()
        for doc, vars in results.get("extracted_variables", {}).items():
            expert = vars.get("expert_name")
            if expert and expert not in ["Not found", "None", "Extraction Failed", None]:
                experts.add(expert)
        
        if experts:
            print(f"\nIdentified {len(experts)} unique experts:")
            for expert in sorted(list(experts)[:10]):
                print(f"  - {expert}")
            if len(experts) > 10:
                print(f"  ... and {len(experts) - 10} more")

def main():
    """Monitor processing until complete"""
    logger.info("Starting monitoring of TBI corpus processing...")
    
    check_count = 0
    while True:
        check_count += 1
        status, results = check_processing_status()
        
        if status is None:
            logger.error(results)
            break
        
        if check_count == 1 or check_count % 5 == 0:  # Print every 5 checks
            print_summary(status, results)
        
        if status['complete']:
            print("\n🎉 Processing is complete! You can now review the output.")
            print("\nNext steps:")
            print("1. Review the extracted metadata in 'tbi_corpus_processing_results.json'")
            print("2. Test search functionality with the processed corpus")
            print("3. Check error logs for any files that failed")
            break
        
        # Wait 30 seconds before next check
        time.sleep(30)

if __name__ == "__main__":
    main()