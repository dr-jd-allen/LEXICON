"""
Process TBI corpus with resume capability - skips already processed files
"""
import os
import json
from pathlib import Path
from document_processor import DocumentProcessor
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_processed_files():
    """Get list of files already processed by checking the collection"""
    try:
        # Check if we have a previous results file
        if os.path.exists("tbi_corpus_processing_results.json"):
            with open("tbi_corpus_processing_results.json", 'r') as f:
                data = json.load(f)
                return set(data.get("processed_files", []))
    except:
        pass
    return set()

def process_tbi_corpus_resume():
    """Process all documents in the TBI corpus, skipping already processed ones"""
    # Load environment variables
    load_dotenv()
    
    # Initialize processor with production collection
    processor = DocumentProcessor(collection_name="lexicon_tbi_corpus")
    
    # Get all supported files
    corpus_dir = Path(r"C:\Users\jdall\lexicon-mvp-alpha\tbi-corpus")
    supported_extensions = ['.pdf', '.docx', '.txt', '.md']
    
    # Get previously processed files
    processed_files = get_processed_files()
    logger.info(f"Found {len(processed_files)} previously processed files")
    
    # Find all files to process
    files_to_process = []
    for ext in supported_extensions:
        for file in corpus_dir.rglob(f"*{ext}"):
            if str(file) not in processed_files:
                files_to_process.append(str(file))
    
    # Skip .wpd files since they're already converted
    wpd_count = len(list(corpus_dir.rglob("*.wpd")))
    if wpd_count > 0:
        logger.info(f"Skipping {wpd_count} .wpd files (use converted PDFs instead)")
    
    logger.info(f"Found {len(files_to_process)} new documents to process")
    
    if not files_to_process:
        logger.info("All documents already processed!")
        return
    
    # Process files one by one for better error handling
    all_results = {
        "processed_files": list(processed_files),
        "extracted_variables": {},
        "vector_ids": [],
        "errors": [],
        "summary": {}
    }
    
    for i, file_path in enumerate(files_to_process, 1):
        logger.info(f"\n[{i}/{len(files_to_process)}] Processing: {Path(file_path).name}")
        
        try:
            results = processor.process_documents([file_path])
            
            if results["processed_files"]:
                all_results["processed_files"].extend(results["processed_files"])
                all_results["extracted_variables"].update(results["extracted_variables"])
                all_results["vector_ids"].extend(results["vector_ids"])
                logger.info(f"✓ Success - created {len(results['vector_ids'])} vectors")
            
            if results["errors"]:
                all_results["errors"].extend(results["errors"])
                logger.error(f"✗ Error: {results['errors'][0]['error']}")
                
        except Exception as e:
            logger.error(f"✗ Failed: {e}")
            all_results["errors"].append({
                "file": file_path,
                "error": str(e)
            })
        
        # Save progress every 10 files
        if i % 10 == 0:
            save_results(all_results)
    
    # Final summary
    all_results["summary"] = {
        "total_files_in_corpus": len(files_to_process) + len(processed_files),
        "previously_processed": len(processed_files),
        "newly_processed": len(all_results["processed_files"]) - len(processed_files),
        "failed": len(all_results["errors"]),
        "total_vectors_created": len(all_results["vector_ids"])
    }
    
    # Save final results
    save_results(all_results)
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("PROCESSING COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Previously processed: {all_results['summary']['previously_processed']}")
    logger.info(f"Newly processed: {all_results['summary']['newly_processed']}")
    logger.info(f"Failed: {all_results['summary']['failed']}")
    logger.info(f"Total vectors in this session: {all_results['summary']['total_vectors_created']}")
    
    # Get total collection count
    total_count = processor.collection.count()
    logger.info(f"Total vectors in collection: {total_count}")

def save_results(results):
    """Save results to file"""
    with open("tbi_corpus_processing_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    logger.info("Progress saved")

if __name__ == "__main__":
    process_tbi_corpus_resume()