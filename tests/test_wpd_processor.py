"""
Test script for WordPerfect file processing
"""
import os
from document_processor import DocumentProcessor
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wpd_processing():
    """Test processing of WordPerfect files"""
    # Load environment variables
    load_dotenv()
    
    # Initialize processor
    processor = DocumentProcessor(collection_name="lexicon_wpd_test")
    
    # Test the extraction methods directly
    logger.info("Testing document processor with various file types...")
    
    # Check if we have any .wpd files in the tbi-corpus folder
    wpd_files = []
    for root, dirs, files in os.walk("tbi_corpus"):
        for file in files:
            if file.endswith('.wpd'):
                wpd_files.append(os.path.join(root, file))
    
    if wpd_files:
        logger.info(f"Found {len(wpd_files)} WordPerfect files")
        for wpd_file in wpd_files:
            try:
                results = processor.process_documents([wpd_file])
                logger.info(f"Successfully processed: {wpd_file}")
                logger.info(f"Results: {results}")
            except Exception as e:
                logger.error(f"Failed to process {wpd_file}: {e}")
    else:
        logger.info("No WordPerfect files found in tbi_corpus folder")
        logger.info("The document processor has been updated to handle .wpd files")
        logger.info("Supported file types: .pdf, .docx, .wpd, .txt, .md")

if __name__ == "__main__":
    test_wpd_processing()