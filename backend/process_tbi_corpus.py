"""
Process all documents in the TBI corpus folder
"""
import os
import json
from pathlib import Path
from document_processor import DocumentProcessor
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_tbi_corpus():
    """Process all documents in the TBI corpus"""
    # Load environment variables
    load_dotenv()
    
    # Initialize processor with production collection
    processor = DocumentProcessor(collection_name="lexicon_tbi_corpus")
    
    # Get all supported files
    corpus_dir = Path(r"C:\Users\jdall\lexicon-mvp-alpha\tbi-corpus")
    supported_extensions = ['.pdf', '.docx', '.wpd', '.txt', '.md']
    
    files_to_process = []
    for ext in supported_extensions:
        files_to_process.extend(corpus_dir.rglob(f"*{ext}"))
    
    # Convert to string paths
    file_paths = [str(f) for f in files_to_process]
    
    logger.info(f"Found {len(file_paths)} documents to process")
    logger.info(f"File types: {', '.join(supported_extensions)}")
    
    # Process in batches to avoid overwhelming the system
    batch_size = 10
    all_results = {
        "processed_files": [],
        "extracted_variables": {},
        "vector_ids": [],
        "errors": [],
        "summary": {}
    }
    
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i+batch_size]
        logger.info(f"\nProcessing batch {i//batch_size + 1} of {(len(file_paths) + batch_size - 1)//batch_size}")
        
        try:
            results = processor.process_documents(batch)
            
            # Merge results
            all_results["processed_files"].extend(results["processed_files"])
            all_results["extracted_variables"].update(results["extracted_variables"])
            all_results["vector_ids"].extend(results["vector_ids"])
            all_results["errors"].extend(results["errors"])
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            for file in batch:
                all_results["errors"].append({
                    "file": file,
                    "error": str(e)
                })
    
    # Final summary
    all_results["summary"] = {
        "total_files": len(file_paths),
        "successfully_processed": len(all_results["processed_files"]),
        "failed": len(all_results["errors"]),
        "total_vectors_created": len(all_results["vector_ids"])
    }
    
    # Save results to file
    results_file = "tbi_corpus_processing_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    
    logger.info(f"\n{'='*60}")
    logger.info("PROCESSING COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Total files: {all_results['summary']['total_files']}")
    logger.info(f"Successfully processed: {all_results['summary']['successfully_processed']}")
    logger.info(f"Failed: {all_results['summary']['failed']}")
    logger.info(f"Total vectors created: {all_results['summary']['total_vectors_created']}")
    logger.info(f"\nResults saved to: {results_file}")
    
    # Print sample of extracted variables
    if all_results["extracted_variables"]:
        logger.info("\n--- Sample Extracted Variables (first 5 documents) ---")
        for i, (filename, vars) in enumerate(list(all_results["extracted_variables"].items())[:5]):
            logger.info(f"\n{filename}:")
            logger.info(f"  Expert: {vars.get('expert_name', 'N/A')}")
            logger.info(f"  Type: {vars.get('document_type', 'N/A')}")
            logger.info(f"  Case: {vars.get('case_name', 'N/A')}")
    
    # Print errors if any
    if all_results["errors"]:
        logger.error(f"\n--- Processing Errors ({len(all_results['errors'])} files) ---")
        for error in all_results["errors"][:10]:  # Show first 10 errors
            logger.error(f"{error['file']}: {error['error']}")

if __name__ == "__main__":
    process_tbi_corpus()