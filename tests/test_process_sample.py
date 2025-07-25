"""
Test processing with a small sample of documents
"""
import os
import json
from pathlib import Path
from document_processor import DocumentProcessor
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sample_processing():
    """Process a small sample of documents"""
    # Load environment variables
    load_dotenv()
    
    # Initialize processor
    processor = DocumentProcessor(collection_name="lexicon_tbi_test")
    
    # Get a few test files of different types
    test_files = [
        r"C:\Users\jdall\lexicon-mvp-alpha\tbi-corpus\processed\Expert CVs\Allen CV 09.2024.pdf",
        r"C:\Users\jdall\lexicon-mvp-alpha\tbi-corpus\processed\Client firm case law precedent\Favorable rulings to plaintiffs + client firm\Ill. R. EVID. 702.docx",
        r"C:\Users\jdall\lexicon-mvp-alpha\tbi-corpus\processed\Client firm case law precedent\Plaintiff counsel strategies\Client firm motions in limine - MIL\MIL - KJA.wpd"
    ]
    
    # Filter to only existing files
    existing_files = [f for f in test_files if os.path.exists(f)]
    
    logger.info(f"Testing with {len(existing_files)} files")
    
    # Process each file individually to better catch errors
    for file_path in existing_files:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {Path(file_path).name}")
        logger.info(f"{'='*60}")
        
        try:
            results = processor.process_documents([file_path])
            
            # Show results
            if results["processed_files"]:
                logger.info("✓ SUCCESS")
                vars = results["extracted_variables"].get(Path(file_path).name, {})
                logger.info(f"Expert: {vars.get('expert_name', 'N/A')}")
                logger.info(f"Type: {vars.get('document_type', 'N/A')}")
                logger.info(f"Date: {vars.get('document_date', 'N/A')}")
                logger.info(f"Vectors created: {len([v for v in results['vector_ids'] if v])}")
            else:
                logger.error("✗ FAILED")
                if results["errors"]:
                    logger.error(f"Error: {results['errors'][0]['error']}")
                    
        except Exception as e:
            logger.error(f"✗ Exception: {e}")

if __name__ == "__main__":
    test_sample_processing()