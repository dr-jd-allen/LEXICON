"""
LEXICON Complete Package - All-in-One Legal AI System
Includes: Document preprocessing, vector database, and AI pipeline
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import shutil

# Core imports
from dotenv import load_dotenv
import anthropic
import openai
from google import generativeai as genai
import chromadb
from chromadb.utils import embedding_functions
import requests

# Document processing
import PyPDF2
import docx
import pypandoc
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========== PART 1: DOCUMENT PROCESSOR ==========

class DocumentProcessor:
    """
    Handles document preprocessing, text extraction, and vector embedding
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
        """Initialize the document processor"""
        # API Keys
        self.anthropic_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.anthropic_key or not self.openai_key:
            raise ValueError("API keys for Anthropic and OpenAI must be provided")
        
        # Model Configuration
        self.anthropic_model = anthropic_model
        self.openai_model = openai_model
        
        # Initialize clients
        self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        
        # Configure embedding function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self.openai_key,
            model_name=self.openai_model
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Connected to existing collection: '{collection_name}'")
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Created new collection: '{collection_name}'")
    
    def process_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """Process a list of documents"""
        logger.info(f"🔄 Processing {len(file_paths)} documents...")
        
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
                
                # Extract text
                if file_path.endswith('.pdf'):
                    text = self._extract_pdf_text(file_path)
                elif file_path.endswith('.docx'):
                    text = self._extract_docx_text(file_path)
                elif file_path.endswith('.wpd'):
                    text = self._extract_wpd_text(file_path)
                else:
                    text = self._extract_text_file(file_path)
                
                logger.info(f"   ✓ Extracted {len(text)} characters")
                
                # Extract metadata using AI
                variables = self._extract_variables(text, file_name)
                results["extracted_variables"][file_name] = variables
                logger.info(f"   ✓ Extracted metadata for: {variables.get('expert_name', 'Unknown')}")
                
                # Create embeddings
                vector_ids = self._create_embeddings(text, file_path, variables)
                results["vector_ids"].extend(vector_ids)
                logger.info(f"   ✓ Created {len(vector_ids)} vectors")
                
                results["processed_files"].append(file_path)
                
            except Exception as e:
                logger.error(f"   ❌ Failed: {e}")
                results["errors"].append({
                    "file": file_path,
                    "error": str(e)
                })
        
        # Summary
        results["summary"] = {
            "total_files": len(file_paths),
            "successfully_processed": len(results["processed_files"]),
            "failed": len(results["errors"]),
            "total_vectors_created": len(results["vector_ids"])
        }
        
        logger.info("✅ Document processing complete")
        return results
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
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
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            return "\n\n".join(para.text for para in doc.paragraphs if para.text.strip())
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {e}")
    
    def _extract_wpd_text(self, file_path: str) -> str:
        """Extract text from WordPerfect files"""
        logger.warning(f"WordPerfect file: {Path(file_path).name} - skipping")
        return f"[WordPerfect file - requires conversion]"
    
    def _extract_text_file(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except:
            # Try latin-1 encoding if utf-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                raise Exception(f"Text extraction failed: {e}")
    
    def _extract_variables(self, text: str, file_name: str) -> Dict[str, Any]:
        """Extract metadata using Claude"""
        text_sample = text[:8000]
        
        prompt = f"""
        Analyze this legal document and extract key information.
        Return ONLY a valid JSON object:
        {{
            "expert_name": "Full name of expert witness",
            "document_type": "deposition/report/motion/affidavit/other",
            "document_date": "YYYY-MM-DD if found",
            "case_name": "Case name or number",
            "key_findings": ["List of key findings"],
            "expert_credentials": ["List of credentials"]
        }}
        
        Document: '{file_name}'
        Text: {text_sample}
        """
        
        try:
            message = self.anthropic_client.messages.create(
                model=self.anthropic_model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text.strip()
            
            # Clean response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return {"expert_name": "Unknown", "error": str(e)}
    
    def _create_embeddings(self, text: str, file_path: str, metadata: Dict) -> List[str]:
        """Create vector embeddings"""
        chunks = self._chunk_text(text, chunk_size=1000, overlap=150)
        
        if not chunks or not text.strip():
            logger.warning(f"No content to embed for {Path(file_path).name}")
            return []
        
        base_id = Path(file_path).stem.replace(" ", "_").replace(".", "_")
        ids = [f"{base_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Create metadata for each chunk
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "source_file": Path(file_path).name,
                "chunk_index": i,
                "total_chunks": len(chunks),
            })
            
            # Ensure proper types
            for key, value in chunk_metadata.items():
                if isinstance(value, list):
                    chunk_metadata[key] = ", ".join(map(str, value))
                elif value is None:
                    chunk_metadata[key] = "N/A"
                elif not isinstance(value, (str, int, float, bool)):
                    chunk_metadata[key] = str(value)
            
            metadatas.append(chunk_metadata)
        
        try:
            self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        except Exception as e:
            raise Exception(f"ChromaDB insertion failed: {e}")
        
        return ids
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
        """Split text into chunks"""
        if not text:
            return []
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
        )
        return text_splitter.split_text(text)
    
    def search_documents(self, query: str, n_results: int = 5, where_filter: Optional[Dict] = None) -> Dict[str, Any]:
        """Search the vector database"""
        try:
            query_params = {
                "query_texts": [query],
                "n_results": n_results
            }
            
            if where_filter:
                query_params["where"] = where_filter
            
            results = self.collection.query(**query_params)
            return {"query": query, "filter": where_filter, "results": results}
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"query": query, "error": str(e), "results": None}


# ========== PART 2: WPD CONVERTER ==========

class WordPerfectConverter:
    """Convert WordPerfect files to PDF using LibreOffice"""
    
    @staticmethod
    def find_wpd_files(corpus_dir: str) -> List[str]:
        """Find all WPD files"""
        wpd_files = []
        for root, dirs, files in os.walk(corpus_dir):
            for file in files:
                if file.lower().endswith('.wpd'):
                    wpd_files.append(os.path.join(root, file))
        return wpd_files
    
    @staticmethod
    def check_libreoffice() -> Optional[str]:
        """Check if LibreOffice is installed"""
        possible_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            r"C:\Program Files\LibreOffice 7\program\soffice.exe",
            r"C:\Program Files\LibreOffice 24.8\program\soffice.exe",
            r"C:\Program Files\LibreOffice 25.2\program\soffice.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        soffice_path = shutil.which("soffice")
        if soffice_path:
            return soffice_path
        
        return None
    
    @staticmethod
    def convert_wpd_to_pdf(wpd_file: str, output_dir: str, soffice_path: str) -> tuple[bool, str]:
        """Convert a single WPD file to PDF"""
        import subprocess
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            cmd = [
                soffice_path,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", output_dir,
                wpd_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                base_name = Path(wpd_file).stem
                pdf_file = os.path.join(output_dir, f"{base_name}.pdf")
                if os.path.exists(pdf_file):
                    return True, pdf_file
                else:
                    return False, "PDF file not created"
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, str(e)


# ========== PART 3: LEXICON PIPELINE ==========

class LEXICONPipeline:
    """Complete LEXICON Pipeline Orchestration"""
    
    def __init__(self):
        # Initialize AI clients
        self.claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai_client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Initialize document processor
        self.doc_processor = DocumentProcessor(collection_name="lexicon_tbi_corpus")
        
        # External database configs
        self.external_databases = {
            "google_scholar": "https://scholar.google.com/scholar?q=",
            "pubmed": "https://pubmed.ncbi.nlm.nih.gov/?term=",
            "courtlistener": "https://www.courtlistener.com/api/rest/v3/search/",
            "arxiv": "https://arxiv.org/search/?query=",
            "firecrawl_api_key": os.getenv("FIRECRAWL_API_KEY")
        }
    
    async def process_case(
        self, 
        target_expert: str, 
        case_strategy: str = "challenge", 
        motion_type: str = "Daubert Motion"
    ) -> Dict[str, Any]:
        """
        Main pipeline entry point
        
        Args:
            target_expert: Name of the expert to analyze
            case_strategy: "challenge" (exclude) or "support" (defend)
            motion_type: Type of motion
        """
        print(f"\n{'='*60}")
        print(f"🎯 LEXICON PIPELINE: Analyzing {target_expert}")
        print(f"📋 Strategy: {case_strategy.upper()} expert")
        print(f"📋 Motion Type: {motion_type}")
        print(f"{'='*60}\n")
        
        # Step 1: Search for expert documents
        print("📚 Step 1: Searching vector database...")
        expert_docs = await self.search_expert_documents(target_expert)
        
        # Step 2: Strategic analysis
        print("\n🧠 Step 2: Developing strategy...")
        case_analysis = await self.orchestrator_analysis(
            expert_docs, target_expert, case_strategy, motion_type
        )
        
        # Step 3: Parallel research
        print("\n🔬 Step 3: Parallel research...")
        research_results = await self.parallel_research(
            case_analysis, expert_docs, case_strategy
        )
        
        # Step 4: Initial brief
        print("\n✍️ Step 4: Drafting brief...")
        initial_brief = await self.forensic_writer_draft(
            case_analysis, research_results, case_strategy, motion_type
        )
        
        # Step 5: Strategic edit
        print("\n📝 Step 5: Strategic enhancement...")
        edited_brief = await self.strategic_edit(
            initial_brief, research_results, case_analysis, case_strategy
        )
        
        # Step 6: Final polish
        print("\n✅ Step 6: Final fact check...")
        final_brief = await self.final_fact_check(edited_brief, expert_docs)
        
        print(f"\n{'='*60}")
        print("✨ PIPELINE COMPLETE!")
        print(f"{'='*60}\n")
        
        return {
            "target_expert": target_expert,
            "case_strategy": case_strategy,
            "motion_type": motion_type,
            "final_brief": final_brief,
            "research": research_results,
            "strategy": case_analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    async def search_expert_documents(self, expert_name: str) -> Dict[str, Any]:
        """Search for expert-related documents"""
        results = self.doc_processor.search_documents(
            query=f"{expert_name} expert testimony deposition report TBI",
            n_results=20
        )
        
        expert_info = {
            "expert_name": expert_name,
            "documents_found": 0,
            "document_types": [],
            "key_findings": [],
            "methodologies": [],
            "credentials": [],
            "relevant_excerpts": []
        }
        
        if results.get('results') and results['results'].get('ids'):
            expert_info['documents_found'] = len(results['results']['ids'][0])
            
            for i in range(len(results['results']['ids'][0])):
                metadata = results['results']['metadatas'][0][i]
                document = results['results']['documents'][0][i]
                
                # Extract document types
                doc_type = metadata.get('document_type', 'other')
                if doc_type not in expert_info['document_types']:
                    expert_info['document_types'].append(doc_type)
                
                # Extract findings and credentials
                if metadata.get('key_findings'):
                    expert_info['key_findings'].extend(
                        [metadata['key_findings']] if isinstance(metadata['key_findings'], str) 
                        else metadata['key_findings']
                    )
                
                if metadata.get('expert_credentials'):
                    expert_info['credentials'].extend(
                        [metadata['expert_credentials']] if isinstance(metadata['expert_credentials'], str)
                        else metadata['expert_credentials']
                    )
                
                # Extract methodologies from text
                if 'DTI' in document or 'diffusion tensor' in document.lower():
                    expert_info['methodologies'].append('DTI imaging')
                if 'neuropsychological' in document.lower():
                    expert_info['methodologies'].append('Neuropsychological testing')
                
                # Save excerpts
                if i < 3:
                    expert_info['relevant_excerpts'].append({
                        'source': metadata.get('source_file', 'Unknown'),
                        'excerpt': document[:500] + '...'
                    })
        
        # Remove duplicates
        expert_info['methodologies'] = list(set(expert_info['methodologies']))
        expert_info['credentials'] = list(set([c for c in expert_info['credentials'] if c]))
        
        print(f"✅ Found {expert_info['documents_found']} documents")
        return expert_info
    
    async def orchestrator_analysis(
        self, 
        expert_docs: Dict, 
        target_expert: str, 
        case_strategy: str, 
        motion_type: str
    ) -> Dict[str, Any]:
        """Strategic analysis by Claude Opus 4"""
        
        if case_strategy == "challenge":
            prompt = f"""
            As Lead Attorney, analyze this expert for {motion_type} to EXCLUDE.
            
            Expert: {target_expert}
            Documents: {expert_docs.get('documents_found', 0)}
            Types: {', '.join(expert_docs.get('document_types', []))}
            Credentials: {json.dumps(expert_docs.get('credentials', []), indent=2)}
            Methods: {json.dumps(expert_docs.get('methodologies', []), indent=2)}
            
            Develop strategy:
            1. Primary vulnerabilities
            2. Daubert factors likely to fail
            3. Research priorities
            4. Key arguments
            5. Anticipated defenses
            """
        else:  # support
            prompt = f"""
            As Lead Attorney, analyze this expert to SUPPORT against {motion_type}.
            
            Expert: {target_expert}
            Documents: {expert_docs.get('documents_found', 0)}
            Types: {', '.join(expert_docs.get('document_types', []))}
            Credentials: {json.dumps(expert_docs.get('credentials', []), indent=2)}
            Methods: {json.dumps(expert_docs.get('methodologies', []), indent=2)}
            
            Develop strategy:
            1. Key strengths
            2. How Daubert factors are met
            3. Research priorities
            4. Preemptive responses
            5. Distinguishing features
            """
        
        response = self.claude.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "strategy": response.content[0].text,
            "expert_profile": expert_docs,
            "case_strategy": case_strategy,
            "motion_type": motion_type
        }
    
    async def parallel_research(
        self, 
        case_analysis: Dict, 
        expert_docs: Dict, 
        case_strategy: str
    ) -> Dict[str, Any]:
        """Execute parallel research"""
        legal_task = self.legal_forensic_research(case_analysis, expert_docs, case_strategy)
        scientific_task = self.scientific_domain_research(case_analysis, expert_docs, case_strategy)
        
        legal_results, scientific_results = await asyncio.gather(legal_task, scientific_task)
        
        return {
            "legal_research": legal_results,
            "scientific_research": scientific_results
        }
    
    async def legal_forensic_research(
        self, 
        case_analysis: Dict, 
        expert_docs: Dict, 
        case_strategy: str
    ) -> Dict[str, Any]:
        """Legal research agent"""
        expert_name = expert_docs.get('expert_name', 'expert')
        
        if case_strategy == "challenge":
            searches = [
                f"Daubert motion exclude {expert_name} TBI",
                f"neuropsychologist expert excluded unreliable",
                f"TBI expert testimony Daubert failure"
            ]
        else:
            searches = [
                f"Daubert motion denied {expert_name} qualified",
                f"neuropsychologist expert admitted reliable",
                f"TBI expert testimony accepted court"
            ]
        
        print("   🔍 Legal research...")
        
        prompt = f"""
        As legal researcher, find {case_strategy} precedents:
        
        Expert: {expert_name}
        Strategy: {case_analysis['strategy'][:1000]}...
        
        Provide:
        1. Relevant cases
        2. Key arguments
        3. Circuit standards
        4. Procedural requirements
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        return {
            "findings": response.choices[0].message.content,
            "search_queries": searches,
            "databases_searched": ["Google Scholar", "Westlaw"],
            "search_strategy": case_strategy
        }
    
    async def scientific_domain_research(
        self, 
        case_analysis: Dict, 
        expert_docs: Dict, 
        case_strategy: str
    ) -> Dict[str, Any]:
        """Scientific research agent"""
        methodologies = expert_docs.get('methodologies', ['neuropsychological testing'])
        
        if case_strategy == "challenge":
            focus = "limitations, false positives, controversies"
        else:
            focus = "validation, reliability, acceptance"
        
        print("   🔬 Scientific research...")
        
        prompt = f"""
        As scientific researcher, analyze {case_strategy}:
        
        Methods: {methodologies}
        Focus: {focus}
        
        Provide scientific evidence for {case_strategy}.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return {
            "findings": response.choices[0].message.content,
            "methodologies_analyzed": methodologies,
            "search_focus": focus,
            "search_strategy": case_strategy
        }
    
    async def forensic_writer_draft(
        self, 
        case_analysis: Dict, 
        research: Dict, 
        case_strategy: str, 
        motion_type: str
    ) -> str:
        """Initial brief writing"""
        
        structure = """
        I. INTRODUCTION
        II. STATEMENT OF FACTS
        III. LEGAL STANDARD
        IV. ARGUMENT
        V. CONCLUSION
        """
        
        prompt = f"""
        Draft {motion_type} to {case_strategy} expert.
        
        Strategy: {case_analysis['strategy'][:2000]}...
        Legal: {research['legal_research']['findings'][:1500]}...
        Scientific: {research['scientific_research']['findings'][:1500]}...
        
        Structure: {structure}
        
        Write formal legal brief.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        
        return response.choices[0].message.content
    
    async def strategic_edit(
        self, 
        initial_brief: str, 
        research: Dict, 
        case_analysis: Dict, 
        case_strategy: str
    ) -> str:
        """Strategic enhancement by Claude"""
        
        if case_strategy == "challenge":
            enhance_prompt = "Make this devastating - highlight every weakness"
        else:
            enhance_prompt = "Make this unassailable - emphasize every strength"
        
        prompt = f"""
        Enhance this brief strategically:
        
        {initial_brief[:4000]}...
        
        {enhance_prompt}
        
        Add power and persuasion.
        """
        
        response = self.claude.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    async def final_fact_check(self, edited_brief: str, expert_docs: Dict) -> str:
        """Final polish and fact check"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Final polish:
            
            {edited_brief}
            
            Check:
            1. Expert name consistency
            2. Citation format
            3. Grammar/spelling
            4. Professional tone
            
            Return polished brief.
            """
            
            response = model.generate_content(prompt)
            return response.text
        except:
            # Return original if fact check fails
            return edited_brief

    async def search_external_database(self, url: str, source: str) -> Optional[str]:
        """Search external databases (placeholder)"""
        logger.info(f"Would search: {source} at {url}")
        return None


# ========== PART 4: COMPLETE SYSTEM ==========

class LEXICONCompleteSystem:
    """
    The complete LEXICON system with all components
    """
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.wpd_converter = WordPerfectConverter()
        self.pipeline = LEXICONPipeline()
        self.corpus_dir = r"C:\Users\jdall\lexicon-mvp-alpha\tbi-corpus"
    
    def prebuild_docker_images(self) -> bool:
        """Pre-build Docker images for faster startup"""
        print("\n🐳 Pre-building Docker images...")
        print("="*60)
        
        # Check if Docker is running
        try:
            result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Docker is not running!")
                print("Please start Docker Desktop and try again.")
                return False
        except FileNotFoundError:
            print("❌ Docker is not installed!")
            return False
        
        print("✅ Docker is running")
        
        # Pull base images
        print("\nStep 1/3: Pulling base images...")
        base_images = [
            "nginx:alpine",
            "chromadb/chroma:latest",
            "redis:7-alpine",
            "alpine:latest",
            "halverneus/static-file-server:latest"
        ]
        
        for image in base_images:
            print(f"  Pulling {image}...")
            result = subprocess.run(['docker', 'pull', image], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  ⚠️  Failed to pull {image}: {result.stderr}")
            else:
                print(f"  ✅ {image} pulled successfully")
        
        # Build webapp image if Dockerfile exists
        print("\nStep 2/3: Building webapp image...")
        dockerfile_path = Path("./Dockerfile")
        if dockerfile_path.exists():
            print("  Building lexicon-webapp:latest...")
            result = subprocess.run(
                ['docker', 'build', '-t', 'lexicon-webapp:latest', '.'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"  ❌ Failed to build webapp image: {result.stderr}")
                return False
            else:
                print("  ✅ lexicon-webapp:latest built successfully")
        else:
            print("  ⚠️  Dockerfile not found, skipping webapp build")
        
        # Pre-create volumes
        print("\nStep 3/3: Pre-creating Docker volumes...")
        volumes = [
            "lexicon-local-storage",
            "lexicon-backups",
            "lexicon-logs"
        ]
        
        for volume in volumes:
            subprocess.run(['docker', 'volume', 'create', volume], capture_output=True)
            print(f"  ✅ Volume {volume} created")
        
        # Display results
        print("\n" + "="*60)
        print("✅ Docker pre-build complete!")
        print("\nCached images:")
        result = subprocess.run(
            ['docker', 'images', '--format', 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}'],
            capture_output=True,
            text=True
        )
        # Filter for relevant images
        for line in result.stdout.split('\n'):
            if any(img in line for img in ['nginx', 'chroma', 'redis', 'lexicon', 'REPOSITORY']):
                print(f"  {line}")
        
        print("\nYour Docker environment is now optimized for faster startup!")
        return True
    
    def setup_environment(self) -> bool:
        """Check environment setup"""
        print("🔧 Checking LEXICON environment...")
        
        # Check API keys
        keys_ok = all([
            os.getenv("ANTHROPIC_API_KEY"),
            os.getenv("OPENAI_API_KEY"),
            os.getenv("GOOGLE_API_KEY")
        ])
        
        if not keys_ok:
            print("❌ Missing API keys in .env file")
            return False
        
        print("✅ API keys configured")
        
        # Check ChromaDB
        try:
            self.doc_processor.collection.count()
            print("✅ ChromaDB connected")
        except:
            print("❌ ChromaDB not running")
            return False
        
        # Check LibreOffice
        soffice = self.wpd_converter.check_libreoffice()
        if soffice:
            print(f"✅ LibreOffice found: {soffice}")
        else:
            print("⚠️  LibreOffice not found (needed for WPD conversion)")
        
        return True
    
    def preprocess_corpus(self, skip_wpd: bool = False) -> Dict[str, Any]:
        """Preprocess the entire corpus"""
        print(f"\n📚 Preprocessing corpus at: {self.corpus_dir}")
        
        # Find all files
        all_files = []
        extensions = ['.pdf', '.docx', '.txt', '.md']
        if not skip_wpd:
            extensions.append('.wpd')
        
        for ext in extensions:
            files = list(Path(self.corpus_dir).rglob(f"*{ext}"))
            all_files.extend([str(f) for f in files])
        
        print(f"Found {len(all_files)} documents")
        
        # Convert WPD files if needed
        wpd_files = [f for f in all_files if f.endswith('.wpd')]
        if wpd_files and not skip_wpd:
            print(f"\n📄 Converting {len(wpd_files)} WordPerfect files...")
            self._convert_wpd_files(wpd_files)
            # Remove WPD from list and add converted PDFs
            all_files = [f for f in all_files if not f.endswith('.wpd')]
            # Add converted PDFs
            converted_dir = os.path.join(self.corpus_dir, "converted_from_wpd")
            if os.path.exists(converted_dir):
                pdf_files = list(Path(converted_dir).rglob("*.pdf"))
                all_files.extend([str(f) for f in pdf_files])
        
        # Process documents
        return self.doc_processor.process_documents(all_files)
    
    def _convert_wpd_files(self, wpd_files: List[str]) -> int:
        """Convert WordPerfect files to PDF"""
        soffice = self.wpd_converter.check_libreoffice()
        if not soffice:
            print("❌ LibreOffice not found - skipping WPD conversion")
            return 0
        
        converted = 0
        output_base = os.path.join(self.corpus_dir, "converted_from_wpd")
        
        for wpd_file in wpd_files:
            rel_path = os.path.relpath(wpd_file, self.corpus_dir)
            rel_dir = os.path.dirname(rel_path)
            output_dir = os.path.join(output_base, rel_dir)
            
            success, result = self.wpd_converter.convert_wpd_to_pdf(
                wpd_file, output_dir, soffice
            )
            if success:
                converted += 1
                print(f"✓ Converted: {Path(wpd_file).name}")
            else:
                print(f"✗ Failed: {Path(wpd_file).name}")
        
        return converted
    
    async def generate_brief(
        self, 
        expert_name: str, 
        strategy: str = "challenge",
        motion_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a legal brief"""
        
        if not motion_type:
            if strategy == "challenge":
                motion_type = "Daubert Motion to Exclude Expert Testimony"
            else:
                motion_type = "Response to Defendant's Daubert Motion"
        
        return await self.pipeline.process_case(
            target_expert=expert_name,
            case_strategy=strategy,
            motion_type=motion_type
        )
    
    def search_corpus(self, query: str, n_results: int = 10) -> Dict[str, Any]:
        """Search the preprocessed corpus"""
        return self.doc_processor.search_documents(query, n_results)
    
    def get_corpus_stats(self) -> Dict[str, Any]:
        """Get statistics about the corpus"""
        try:
            count = self.doc_processor.collection.count()
            return {
                "total_vectors": count,
                "collection_name": "lexicon_tbi_corpus",
                "status": "active"
            }
        except:
            return {
                "total_vectors": 0,
                "collection_name": "lexicon_tbi_corpus",
                "status": "error"
            }


# ========== PART 5: CLI INTERFACE ==========

async def main():
    """Main CLI interface for LEXICON"""
    system = LEXICONCompleteSystem()
    
    print("\n" + "="*80)
    print("🏛️  LEXICON COMPLETE LEGAL AI SYSTEM")
    print("="*80)
    print("Unified package for document processing and legal brief generation")
    print("="*80 + "\n")
    
    # Check environment
    if not system.setup_environment():
        print("\n❌ Please fix environment issues before continuing")
        return
    
    # Get corpus stats
    stats = system.get_corpus_stats()
    print(f"\n📊 Corpus Status: {stats['total_vectors']} vectors in database")
    
    while True:
        print("\n" + "-"*60)
        print("MAIN MENU:")
        print("1. Preprocess new documents")
        print("2. Search the corpus")
        print("3. Generate legal brief (support expert)")
        print("4. Generate legal brief (challenge expert)")
        print("5. View corpus statistics")
        print("6. Pre-build Docker images")
        print("7. Exit")
        print("-"*60)
        
        choice = input("\nSelect option (1-7): ")
        
        if choice == "1":
            # Preprocess documents
            print("\nPreprocess options:")
            print("1. Process all documents (including WPD conversion)")
            print("2. Skip WordPerfect files")
            
            sub_choice = input("\nSelect (1-2): ")
            skip_wpd = sub_choice == "2"
            
            results = system.preprocess_corpus(skip_wpd=skip_wpd)
            print(f"\n✅ Processed {results['summary']['successfully_processed']} documents")
            print(f"❌ Failed: {results['summary']['failed']}")
            print(f"📊 Total vectors: {results['summary']['total_vectors_created']}")
            
        elif choice == "2":
            # Search corpus
            query = input("\nEnter search query: ")
            results = system.search_corpus(query)
            
            if results.get('results'):
                print(f"\nFound {len(results['results']['ids'][0])} results:")
                for i in range(min(3, len(results['results']['ids'][0]))):
                    print(f"\n{i+1}. {results['results']['metadatas'][0][i].get('source_file', 'Unknown')}")
                    print(f"   {results['results']['documents'][0][i][:200]}...")
            
        elif choice in ["3", "4"]:
            # Generate brief
            strategy = "support" if choice == "3" else "challenge"
            
            print(f"\n{'SUPPORT' if strategy == 'support' else 'CHALLENGE'} EXPERT MODE")
            expert = input("Enter expert name: ")
            
            print("\nGenerating brief...")
            result = await system.generate_brief(expert, strategy)
            
            # Save brief
            output_dir = Path("./lexicon-output/briefs")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{strategy}_{expert.replace(' ', '_')}_{timestamp}.txt"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result['final_brief'])
            
            print(f"\n✅ Brief saved to: {filepath}")
            print(f"📄 Length: {len(result['final_brief'])} characters")
            
        elif choice == "5":
            # Statistics
            stats = system.get_corpus_stats()
            print(f"\n📊 CORPUS STATISTICS:")
            print(f"   Total vectors: {stats['total_vectors']}")
            print(f"   Collection: {stats['collection_name']}")
            print(f"   Status: {stats['status']}")
            
        elif choice == "6":
            # Pre-build Docker images
            success = system.prebuild_docker_images()
            if success:
                print("\n✅ Docker images pre-built successfully!")
            else:
                print("\n❌ Docker pre-build failed. Please check the errors above.")
            
        elif choice == "7":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())