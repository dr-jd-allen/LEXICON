"""
Show illustrative examples of what's stored in the vector database
"""
import json
from document_processor import DocumentProcessor
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_vector_examples():
    """Display examples of stored vectors with metadata and content"""
    load_dotenv()
    processor = DocumentProcessor(collection_name="lexicon_tbi_corpus")
    
    print("\n" + "="*80)
    print("ILLUSTRATIVE EXAMPLES OF VECTOR DATABASE CONTENT")
    print("="*80)
    
    # Example 1: Search for neuroimaging content
    print("\n1. EXAMPLE SEARCH: 'neuroimaging fMRI DTI brain injury diagnosis'")
    print("-" * 60)
    
    results = processor.search_documents(
        "neuroimaging fMRI DTI brain injury diagnosis",
        n_results=3
    )
    
    if results and results.get('results'):
        for i, (doc, metadata, distance) in enumerate(zip(
            results['results']['documents'][0],
            results['results']['metadatas'][0],
            results['results']['distances'][0]
        ), 1):
            print(f"\nRESULT {i}:")
            print(f"Relevance Score: {1 - distance:.3f}")
            print(f"\nMETADATA:")
            print(f"  Source File: {metadata.get('source_file', 'N/A')}")
            print(f"  Expert Name: {metadata.get('expert_name', 'N/A')}")
            print(f"  Document Type: {metadata.get('document_type', 'N/A')}")
            print(f"  Document Date: {metadata.get('document_date', 'N/A')}")
            print(f"  Case Name: {metadata.get('case_name', 'N/A')}")
            print(f"  Expert Credentials: {metadata.get('expert_credentials', 'N/A')}")
            print(f"  Key Findings: {metadata.get('key_findings', 'N/A')}")
            print(f"  Chunk: {metadata.get('chunk_index', 0) + 1} of {metadata.get('total_chunks', 'N/A')}")
            print(f"\nCONTENT EXCERPT:")
            print(f"  {doc[:300]}...")
    
    # Example 2: Search for expert testimony
    print("\n\n2. EXAMPLE SEARCH: 'expert witness testimony traumatic brain injury'")
    print("-" * 60)
    
    results = processor.search_documents(
        "expert witness testimony traumatic brain injury mild TBI",
        n_results=3
    )
    
    if results and results.get('results'):
        for i, (doc, metadata, distance) in enumerate(zip(
            results['results']['documents'][0],
            results['results']['metadatas'][0],
            results['results']['distances'][0]
        ), 1):
            print(f"\nRESULT {i}:")
            print(f"Relevance Score: {1 - distance:.3f}")
            print(f"\nMETADATA:")
            print(f"  Source File: {metadata.get('source_file', 'N/A')}")
            print(f"  Expert Name: {metadata.get('expert_name', 'N/A')}")
            print(f"  Document Type: {metadata.get('document_type', 'N/A')}")
            print(f"\nCONTENT EXCERPT:")
            print(f"  {doc[:300]}...")
    
    # Example 3: Show extracted metadata variety
    print("\n\n3. METADATA EXTRACTION EXAMPLES")
    print("-" * 60)
    
    # Load the processing results to show variety
    with open('tbi_corpus_processing_results.json', 'r') as f:
        results = json.load(f)
    
    # Show a few different document types
    examples = []
    seen_types = set()
    for filename, metadata in results.get('extracted_variables', {}).items():
        doc_type = metadata.get('document_type', 'other')
        if doc_type not in seen_types and len(examples) < 5:
            examples.append((filename, metadata))
            seen_types.add(doc_type)
    
    for filename, metadata in examples:
        print(f"\nFile: {filename}")
        print(f"  Expert: {metadata.get('expert_name', 'N/A')}")
        print(f"  Type: {metadata.get('document_type', 'N/A')}")
        print(f"  Date: {metadata.get('document_date', 'N/A')}")
        print(f"  Case: {metadata.get('case_name', 'N/A')}")
        if metadata.get('key_findings'):
            findings = metadata['key_findings']
            if isinstance(findings, list) and findings:
                print(f"  Key Finding: {findings[0][:100]}...")
    
    # Show unique experts found
    print("\n\n4. UNIQUE EXPERTS IDENTIFIED")
    print("-" * 60)
    experts = set()
    for metadata in results.get('extracted_variables', {}).values():
        expert = metadata.get('expert_name')
        if expert and expert not in ['Not found', 'None', 'N/A', 'Extraction Failed']:
            experts.add(expert)
    
    print(f"Total unique experts found: {len(experts)}")
    for i, expert in enumerate(sorted(list(experts))[:10], 1):
        print(f"  {i}. {expert}")
    if len(experts) > 10:
        print(f"  ... and {len(experts) - 10} more experts")
    
    # Show document type distribution
    print("\n\n5. DOCUMENT TYPE DISTRIBUTION")
    print("-" * 60)
    type_counts = {}
    for metadata in results.get('extracted_variables', {}).values():
        doc_type = metadata.get('document_type', 'other')
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
    
    for doc_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {doc_type}: {count} documents")

if __name__ == "__main__":
    show_vector_examples()