"""
Document Preprocessor for LEXICON Legal AI System
Handles PDF parsing, text extraction, and vector embedding
(Revised for better configuration and logging)
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Load environment variables for scripts that use this class
from dotenv import load_dotenv
import anthropic
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
import docx
import pypandoc

# Configure logging to provide informative output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    A robust document processing system that extracts text from legal documents,
    enriches it with AI-generated metadata, and creates vector embeddings for search.
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        chroma_host: str = "localhost",
        chroma_port: int = 8000,
        collection_name: str = "lexicon_legal_docs",
        openai_model: str = "text-embedding-ada-002",
        anthropic_model: str = "claude-opus-4-20250514",
    ):
        """
        Initializes the processor with a flexible configuration.

        Args:
            anthropic_api_key (Optional[str]): Anthropic API key. Falls back to env var 'ANTHROPIC_API_KEY'.
            openai_api_key (Optional[str]): OpenAI API key. Falls back to env var 'OPENAI_API_KEY'.
            chroma_host (str): The hostname for the ChromaDB server.
            chroma_port (int): The port for the ChromaDB server.
            collection_name (str): The name of the ChromaDB collection to use.
            openai_model (str): The model name for OpenAI embeddings.
            anthropic_model (str): The model name for Anthropic metadata extraction.
        """
        # API Keys: Use provided key or fall back to environment variables
        self.anthropic_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.anthropic_key or not self.openai_key:
            raise ValueError("API keys for Anthropic and OpenAI must be provided or set as environment variables.")

        # Model Configuration
        self.anthropic_model = anthropic_model
        self.openai_model = openai_model
        
        # Initialize API and DB Clients
        self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

        # Configure embedding function for ChromaDB
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self.openai_key,
            model_name=self.openai_model
        )

        # Get or create the ChromaDB collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Connected to existing ChromaDB collection: '{collection_name}'")
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Created new ChromaDB collection: '{collection_name}'")

    def process_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Main entry point for processing a list of documents. It orchestrates text extraction,
        metadata generation, chunking, and vector embedding.
        """
        logger.info(f"🔄 Starting processing for {len(file_paths)} documents...")
        
        results = {
            "processed_files": [],
            "extracted_variables": {},
            "vector_ids": [],
            "errors": [],
            "summary": {}
        }
        
        for file_path in file_paths:
            try:
                file_name = Path(file_path).name
                logger.info(f"📄 Processing: {file_name}")
                
                # Step 1: Extract text based on file type
                if file_path.endswith('.pdf'):
                    text = self._extract_pdf_text(file_path)
                elif file_path.endswith('.docx'):
                    text = self._extract_docx_text(file_path)
                elif file_path.endswith('.wpd'):
                    text = self._extract_wpd_text(file_path)
                else:
                    text = self._extract_text_file(file_path)
                logger.info(f"   ✓ Extracted {len(text)} characters from {file_name}")
                
                # Step 2: Extract key variables using Claude
                variables = self._extract_variables(text, file_name)
                results["extracted_variables"][file_name] = variables
                logger.info(f"   ✓ Extracted variables for expert: {variables.get('expert_name', 'Unknown')}")
                
                # Step 3: Create and store vector embeddings
                vector_ids = self._create_embeddings(text, file_path, variables)
                results["vector_ids"].extend(vector_ids)
                logger.info(f"   ✓ Created {len(vector_ids)} vector embeddings for {file_name}")
                
                results["processed_files"].append(file_path)
                
            except Exception as e:
                logger.error(f"   ❌ Failed to process {file_path}. Error: {e}", exc_info=True)
                results["errors"].append({
                    "file": file_path,
                    "error": str(e)
                })
        
        # Final summary statistics
        results["summary"] = {
            "total_files": len(file_paths),
            "successfully_processed": len(results["processed_files"]),
            "failed": len(results["errors"]),
            "total_vectors_created": len(results["vector_ids"])
        }
        logger.info("✅ Document processing complete.")
        return results

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extracts text from a PDF file, including page numbers."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        except Exception as e:
            raise Exception(f"PDF extraction failed: {e}")
        return text

    def _extract_docx_text(self, file_path: str) -> str:
        """Extracts text from a DOCX file."""
        try:
            doc = docx.Document(file_path)
            return "\n\n".join(para.text for para in doc.paragraphs if para.text.strip())
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {e}")

    def _extract_text_file(self, file_path: str) -> str:
        """Extracts text from a plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Text file extraction failed: {e}")
    
    def _extract_wpd_text(self, file_path: str) -> str:
        """Extracts text from a WordPerfect (.wpd) file."""
        logger.warning(f"WordPerfect (.wpd) files require specialized conversion tools.")
        logger.warning(f"Skipping: {Path(file_path).name}")
        # For now, return a placeholder. In production, you'd use:
        # - LibreOffice command line conversion
        # - Commercial WPD converters
        # - Or pre-convert WPD files to PDF/DOCX
        return f"[WordPerfect file: {Path(file_path).name} - conversion not implemented]"

    def _extract_variables(self, text: str, file_name: str) -> Dict[str, Any]:
        """Extracts key structured variables from text using the Anthropic API."""
        text_sample = text[:8000] # Use a larger sample for better context
        
        prompt = f"""
        Analyze the following legal document excerpt and extract the specified key information.
        Return your answer as a single, valid JSON object with the keys shown below.

        JSON structure:
        {{
            "expert_name": "Full name of the primary expert witness",
            "document_type": "Classify as one of: deposition, report, motion, affidavit, or other",
            "document_date": "Document date if found (format as YYYY-MM-DD)",
            "case_name": "Case name or number if found",
            "key_findings": ["List of key medical or technical findings, if any"],
            "expert_credentials": ["List of the expert's relevant credentials mentioned"]
        }}

        Document excerpt from '{file_name}':
        ---
        {text_sample}
        ---

        Return ONLY the JSON object. Do not include any other text, comments, or markdown.
        """
        
        try:
            message = self.anthropic_client.messages.create(
                model=self.anthropic_model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text.strip()
            
            # Clean up potential markdown code fences
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.warning(f"   ⚠️ AI variable extraction failed for {file_name}: {e}")
            return { "expert_name": "Extraction Failed", "error": str(e) }

    def _create_embeddings(self, text: str, file_path: str, metadata: Dict) -> List[str]:
        """Chunks text and creates vector embeddings in ChromaDB with rich metadata."""
        chunks = self._chunk_text(text, chunk_size=1000, overlap=150)
        
        # Handle empty documents
        if not chunks or not text.strip():
            logger.warning(f"   ⚠️ No content to embed for {Path(file_path).name}")
            return []
        
        base_id = Path(file_path).stem.replace(" ", "_").replace(".", "_")
        ids = [f"{base_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Create metadata for each chunk, ensuring it's serializable for ChromaDB
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy() # Start with AI-extracted variables
            chunk_metadata.update({
                "source_file": Path(file_path).name,
                "chunk_index": i,
                "total_chunks": len(chunks),
            })
            # Ensure all metadata values are valid types (str, int, float, bool)
            for key, value in chunk_metadata.items():
                if isinstance(value, list):
                    chunk_metadata[key] = ", ".join(map(str, value)) # Convert lists to strings
                elif value is None:
                    chunk_metadata[key] = "N/A"  # Replace None with string
                elif not isinstance(value, (str, int, float, bool)):
                    chunk_metadata[key] = str(value)  # Convert other types to string
            metadatas.append(chunk_metadata)
        
        try:
            self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        except Exception as e:
            raise Exception(f"ChromaDB insertion failed: {e}")
            
        return ids

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
        """Splits text into overlapping chunks, attempting to respect sentence boundaries."""
        if not text:
            return []
        
        # Use recursive character text splitter for more robust chunking
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""] # Prioritize logical breaks
        )
        return text_splitter.split_text(text)

    def search_documents(self, query: str, n_results: int = 5, where_filter: Optional[Dict] = None) -> Dict[str, Any]:
        """Searches the vector database for relevant document chunks."""
        try:
            # Build query parameters
            query_params = {
                "query_texts": [query],
                "n_results": n_results
            }
            
            # Only add where filter if it's provided and not empty
            if where_filter:
                query_params["where"] = where_filter
                
            results = self.collection.query(**query_params)
            return { "query": query, "filter": where_filter, "results": results }
        except Exception as e:
            logger.error(f"Search query failed: {e}", exc_info=True)
            return { "query": query, "error": str(e), "results": None }

# --- Test Functions ---
def test_document_processor():
    """Tests the document processor with a sample file."""
    logger.info("🚀 Testing LEXICON Document Processor 🚀")
    
    # Load API keys from .env file in the current directory
    load_dotenv()
    
    # Create test documents if they don't exist
    test_dir = Path("./tbi_corpus")
    test_dir.mkdir(exist_ok=True)
    sample_file = test_dir / "sample_expert_report.txt"
    
    if not sample_file.exists():
        sample_content = """
        EXPERT WITNESS REPORT - CONFIDENTIAL

        Case Name: Johnson v. Statewide Trucking
        Case No: 2025-CV-01234
        Date of Report: July 15, 2025

        Prepared by: Dr. Evelyn Reed, M.D., Ph.D.
        Credentials:
        - Board Certified Neurologist
        - Ph.D. in Neuroscience, Johns Hopkins University
        - Director of the Traumatic Brain Injury Center at City General Hospital

        METHODOLOGY:
        A comprehensive neurological examination was performed on the plaintiff, Mr. Johnson. 
        This included a physical examination, review of medical records, and advanced neuroimaging (fMRI and DTI). 
        The primary assessment tool used was the Glasgow Coma Scale (GCS) at the time of the accident,
        supplemented by the Post-Concussion Symptom Scale (PCSS) during follow-up visits.

        KEY FINDINGS:
        1. Neuroimaging reveals diffuse axonal injury (DAI) in the white matter tracts.
        2. Mr. Johnson exhibits significant deficits in executive function and processing speed.
        3. Persistent symptoms include chronic headaches, memory loss, and vertigo.

        CONCLUSION:
        It is my professional opinion, to a reasonable degree of medical certainty, that Mr. Johnson
        suffered a moderate-to-severe traumatic brain injury (TBI) as a direct result of the
        motor vehicle collision on January 5, 2025.
        """
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        logger.info(f"Created sample file: {sample_file}")

    try:
        # Initialize the processor (it will use the loaded env vars)
        processor = DocumentProcessor(collection_name="lexicon_test_collection")
        
        # Process the document
        test_files = [str(f) for f in test_dir.glob("*.txt")]
        if test_files:
            results = processor.process_documents(test_files)
            
            logger.info("\n📊 --- Processing Summary --- 📊")
            logger.info(json.dumps(results["summary"], indent=2))
            
            logger.info("\n🔍 --- Extracted Variables --- 🔍")
            logger.info(json.dumps(results["extracted_variables"], indent=2))
            
            # Test search functionality
            logger.info("\n🔎 --- Testing Search Functionality --- 🔎")
            query = "What neuroimaging techniques were used to assess the patient?"
            search_results = processor.search_documents(query, n_results=2)
            logger.info(f"Query: {query}")
            logger.info(json.dumps(search_results["results"], indent=2))
            
            # Test filtered search
            logger.info("\n🔎 --- Testing Filtered Search --- 🔎")
            filter_query = "What were the key findings?"
            filter_condition = {"expert_name": "Dr. Evelyn Reed, M.D., Ph.D."}
            filtered_results = processor.search_documents(filter_query, n_results=2, where_filter=filter_condition)
            logger.info(f"Query: {filter_query} | Filter: {filter_condition}")
            logger.info(json.dumps(filtered_results["results"], indent=2))

        else:
            logger.warning("No test files found to process.")

    except Exception as e:
        logger.error(f"An error occurred during the test run: {e}", exc_info=True)


if __name__ == "__main__":
    test_document_processor()