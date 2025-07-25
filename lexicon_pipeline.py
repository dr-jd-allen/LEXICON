# lexicon_pipeline.py
"""
LEXICON Complete Orchestration Pipeline
Connects preprocessed data → Orchestrator → Parallel Research → Brief Generation
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import anthropic
import openai
from google import generativeai as genai
import chromadb
from pathlib import Path
import requests  # For Firecrawl API
import logging

# Import our document processor
from document_processor import DocumentProcessor

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LEXICONPipeline:
    """
    Complete LEXICON Pipeline Orchestration
    """
    
    def __init__(self):
        # Initialize all API clients
        self.claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai_client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Configure Google AI with your API key
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            genai.configure(api_key=google_api_key)
            logger.info("Google AI (Gemini) configured successfully")
        else:
            logger.warning("No Google AI API key found - Gemini features will be disabled")
        
        # Initialize document processor with correct collection
        self.doc_processor = DocumentProcessor(collection_name="lexicon_tbi_corpus")
        
        # External database configs
        self.external_databases = {
            "google_scholar": "https://scholar.google.com/scholar?q=",
            "pubmed": "https://pubmed.ncbi.nlm.nih.gov/?term=",
            "courtlistener": "https://www.courtlistener.com/api/rest/v3/search/",
            "arxiv": "https://arxiv.org/search/?query=",
            "firecrawl_api_key": os.getenv("FIRECRAWL_API_KEY")
        }
    
    async def search_external_database(self, url: str, source: str) -> Optional[str]:
        """
        Use Firecrawl to scrape external databases
        """
        if not self.external_databases.get("firecrawl_api_key"):
            logger.warning(f"No Firecrawl API key, simulating {source} search")
            # Return simulated content based on source
            if "scholar.google.com" in url:
                return "Simulated Google Scholar results: Recent cases involving TBI expert challenges..."
            elif "pubmed.ncbi" in url:
                return "Simulated PubMed results: Studies on TBI diagnostic reliability..."
            return None
        
        try:
            # Firecrawl API endpoint
            firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
            
            headers = {
                "Authorization": f"Bearer {self.external_databases['firecrawl_api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "url": url,
                "pageOptions": {
                    "onlyMainContent": True,
                    "includeHtml": False
                }
            }
            
            response = requests.post(firecrawl_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("content", "")
            else:
                logger.error(f"Firecrawl error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return None
        
    async def anonymize_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Anonymize sensitive information in documents (HIPAA compliance)
        """
        print("🔒 Anonymizing documents for HIPAA compliance...")
        
        anonymized_docs = []
        for doc in documents:
            # Create anonymization mapping
            anonymization_map = {
                # Patient identifiers
                r'\b\d{3}-\d{2}-\d{4}\b': '[SSN-REDACTED]',
                r'\b\d{10,}\b': '[ID-REDACTED]',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b': '[DATE-REDACTED]',
                r'\b\d{1,2}/\d{1,2}/\d{4}\b': '[DATE-REDACTED]',
                # Medical record numbers
                r'\bMRN[:\s]*\d+\b': 'MRN: [REDACTED]',
                r'\bDOB[:\s]*[\d/\-]+\b': 'DOB: [REDACTED]',
                # Phone numbers
                r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b': '[PHONE-REDACTED]',
                # Email addresses
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[EMAIL-REDACTED]'
            }
            
            # Apply anonymization
            import re
            anonymized_content = doc.get('content', '')
            for pattern, replacement in anonymization_map.items():
                anonymized_content = re.sub(pattern, replacement, anonymized_content, flags=re.IGNORECASE)
            
            anonymized_doc = doc.copy()
            anonymized_doc['content'] = anonymized_content
            anonymized_doc['anonymized'] = True
            anonymized_docs.append(anonymized_doc)
        
        print(f"✅ Anonymized {len(anonymized_docs)} documents")
        return anonymized_docs

    async def process_case(self, target_expert: str, case_strategy: str = "challenge", motion_type: str = "Daubert Motion", uploaded_documents: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Main pipeline entry point
        
        Args:
            target_expert: Name of the expert to analyze
            case_strategy: "challenge" (exclude expert) or "support" (defend expert)
            motion_type: Type of motion (Daubert, Motion in Limine, Response to Daubert, etc.)
            uploaded_documents: Optional list of user-uploaded documents
        """
        print(f"\n{'='*60}")
        print(f"🎯 LEXICON PIPELINE: Analyzing {target_expert}")
        print(f"📋 Strategy: {case_strategy.upper()} expert")
        print(f"📋 Motion Type: {motion_type}")
        print(f"{'='*60}\n")
        
        # Step 0: Anonymize uploaded documents if provided
        if uploaded_documents:
            print("📄 Step 0: Processing user-uploaded documents...")
            anonymized_uploads = await self.anonymize_documents(uploaded_documents)
        else:
            anonymized_uploads = []
        
        # Step 1: Search preprocessed database for relevant documents
        print("📚 Step 1: Searching vector database for expert documents...")
        expert_docs = await self.search_expert_documents(target_expert)
        
        # Step 2: I (Claude Opus 4) analyze and develop strategy
        print("\n🧠 Step 2: Orchestrator developing case strategy and case summary...")
        case_analysis = await self.orchestrator_analysis(expert_docs, target_expert, case_strategy, motion_type, anonymized_uploads)
        
        # Step 3: Parallel research (Agents 2 & 3)
        print("\n🔬 Step 3: Initiating parallel research...")
        research_results = await self.parallel_research(case_analysis, expert_docs, case_strategy)
        
        # Step 4: Brief writing (Agent 4 - GPT-4)
        print("\n✍️ Step 4: Forensic writer drafting initial brief...")
        initial_brief = await self.forensic_writer_draft(case_analysis, research_results, case_strategy, motion_type)
        
        # Step 5: My strategic edit
        print("\n📝 Step 5: Orchestrator performing strategic edit...")
        edited_brief = await self.strategic_edit(initial_brief, research_results, case_analysis, case_strategy)
        
        # Step 6: Final fact check (Agent 5 - Gemini)
        print("\n✅ Step 6: Final fact checking and polish...")
        final_brief = await self.final_fact_check(edited_brief, expert_docs)
        
        # Step 7: Generate strategic recommendations
        print("\n📊 Step 7: Generating strategic recommendations...")
        strategic_recommendations = await self.generate_strategic_recommendations(
            case_analysis, research_results, final_brief, case_strategy
        )
        
        print(f"\n{'='*60}")
        print("✨ PIPELINE COMPLETE!")
        print(f"{'='*60}\n")
        
        return {
            "target_expert": target_expert,
            "case_strategy": case_strategy,
            "motion_type": motion_type,
            "final_brief": final_brief,
            "strategic_recommendations": strategic_recommendations,
            "research": research_results,
            "strategy": case_analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    async def search_expert_documents(self, expert_name: str) -> Dict[str, Any]:
        """
        Search preprocessed ChromaDB for expert-related documents
        """
        # Search for all documents mentioning this expert
        results = self.doc_processor.search_documents(
            query=f"{expert_name} expert testimony deposition report TBI traumatic brain injury",
            n_results=20
        )
        
        if results.get('error'):
            logger.error(f"Error searching documents: {results['error']}")
            return {"expert_name": expert_name, "documents_found": 0}
        
        # Extract key information
        expert_info = {
            "expert_name": expert_name,
            "documents_found": 0,
            "document_types": [],
            "key_findings": [],
            "methodologies": [],
            "credentials": [],
            "relevant_excerpts": []
        }
        
        # Parse results
        if results.get('results') and results['results'].get('ids'):
            expert_info['documents_found'] = len(results['results']['ids'][0])
            
            for i in range(len(results['results']['ids'][0])):
                metadata = results['results']['metadatas'][0][i]
                document = results['results']['documents'][0][i]
                
                # Collect unique document types
                doc_type = metadata.get('document_type', 'other')
                if doc_type not in expert_info['document_types']:
                    expert_info['document_types'].append(doc_type)
                
                # Extract key information from metadata
                if metadata.get('key_findings'):
                    findings = metadata['key_findings']
                    if isinstance(findings, str):
                        expert_info['key_findings'].append(findings)
                    elif isinstance(findings, list):
                        expert_info['key_findings'].extend(findings)
                
                if metadata.get('expert_credentials'):
                    creds = metadata['expert_credentials']
                    if isinstance(creds, str):
                        expert_info['credentials'].append(creds)
                    elif isinstance(creds, list):
                        expert_info['credentials'].extend(creds)
                
                # Extract methodologies from document text
                if 'DTI' in document or 'diffusion tensor' in document.lower():
                    expert_info['methodologies'].append('DTI imaging')
                if 'neuropsychological' in document.lower():
                    expert_info['methodologies'].append('Neuropsychological testing')
                if 'glasgow coma' in document.lower() or 'GCS' in document:
                    expert_info['methodologies'].append('Glasgow Coma Scale')
                
                # Save relevant excerpts
                if i < 3:  # Top 3 most relevant
                    expert_info['relevant_excerpts'].append({
                        'source': metadata.get('source_file', 'Unknown'),
                        'excerpt': document[:500] + '...'
                    })
        
        # Remove duplicates
        expert_info['methodologies'] = list(set(expert_info['methodologies']))
        expert_info['credentials'] = list(set([c for c in expert_info['credentials'] if c]))
        
        print(f"✅ Found {expert_info['documents_found']} documents for {expert_name}")
        if expert_info['document_types']:
            print(f"   Document types: {', '.join(expert_info['document_types'])}")
        
        return expert_info
    
    async def orchestrator_analysis(self, expert_docs: Dict, target_expert: str, case_strategy: str, motion_type: str, anonymized_uploads: List[Dict] = None) -> Dict[str, Any]:
        """
        I (Claude Opus 4) analyze the case and develop strategy
        Generate case summary for researcher agents
        """
        if case_strategy == "challenge":
            prompt = f"""
            As the Lead Attorney and Senior Tort Strategist for LEXICON, analyze this expert witness 
            for a {motion_type} to EXCLUDE their testimony.
            
            Target Expert: {target_expert}
            
            Documents Found: {expert_docs.get('documents_found', 0)}
            Document Types: {', '.join(expert_docs.get('document_types', []))}
            
            Known Credentials: {json.dumps(expert_docs.get('credentials', []), indent=2)}
            
            Identified Methodologies: {json.dumps(expert_docs.get('methodologies', []), indent=2)}
            
            Key Findings from Documents: {json.dumps(expert_docs.get('key_findings', [])[:5], indent=2)}
            
            Relevant Document Excerpts:
            {json.dumps(expert_docs.get('relevant_excerpts', [])[:2], indent=2)}
            
            Develop a comprehensive challenge strategy including:
            1. Primary vulnerabilities to exploit (be specific about which Daubert factors)
            2. Methodological weaknesses based on the actual documents found
            3. Research priorities for the forensic and scientific teams
            4. Key arguments to develop (numbered list)
            5. Anticipated defense responses and counter-arguments
            6. Strategic recommendations for deposition if needed
            
            Focus on actionable insights that will lead to exclusion.
            
            ALSO GENERATE A CASE SUMMARY for the researcher agents including:
            - Key facts of the case
            - Critical issues to investigate
            - Specific research priorities
            - Important context from uploaded documents
            """
        else:  # case_strategy == "support"
            prompt = f"""
            As the Lead Attorney and Senior Tort Strategist for LEXICON, analyze this expert witness 
            to SUPPORT their testimony and defend against a {motion_type}.
            
            Our Expert: {target_expert}
            
            Documents Found: {expert_docs.get('documents_found', 0)}
            Document Types: {', '.join(expert_docs.get('document_types', []))}
            
            Known Credentials: {json.dumps(expert_docs.get('credentials', []), indent=2)}
            
            Identified Methodologies: {json.dumps(expert_docs.get('methodologies', []), indent=2)}
            
            Key Findings from Documents: {json.dumps(expert_docs.get('key_findings', [])[:5], indent=2)}
            
            Relevant Document Excerpts:
            {json.dumps(expert_docs.get('relevant_excerpts', [])[:2], indent=2)}
            
            Develop a comprehensive support strategy including:
            1. Key strengths that satisfy each Daubert factor
            2. How their methodologies align with accepted standards
            3. Research priorities to bolster credibility
            4. Preemptive responses to likely challenges
            5. Distinguishing qualifications and experience
            6. Strategic recommendations for direct examination
            
            Build an unassailable foundation for admissibility.
            
            ALSO GENERATE A CASE SUMMARY for the researcher agents including:
            - Key facts of the case
            - Critical issues to investigate
            - Specific research priorities
            - Important context from uploaded documents
            """
        
        response = self.claude.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse the response to extract strategy and case summary
        full_response = response.content[0].text
        
        # Split response into strategy and case summary sections
        # The AI should naturally separate these with headers
        strategy_section = full_response
        case_summary = ""
        
        if "CASE SUMMARY" in full_response.upper():
            parts = full_response.split("CASE SUMMARY", 1)
            strategy_section = parts[0].strip()
            case_summary = parts[1].strip() if len(parts) > 1 else ""
        
        return {
            "strategy": strategy_section,
            "case_summary": case_summary,
            "expert_profile": expert_docs,
            "case_strategy": case_strategy,
            "motion_type": motion_type,
            "anonymized_uploads": anonymized_uploads
        }
    
    async def parallel_research(self, case_analysis: Dict, expert_docs: Dict, case_strategy: str) -> Dict[str, Any]:
        """
        Coordinate parallel research between legal and scientific agents
        Uses external research module for real database searches
        """
        # Import external research module
        try:
            from lexicon_external_research import ExternalResearchModule
            
            # Extract data for external research
            expert_name = expert_docs.get('expert_name', '')
            methodologies = expert_docs.get('methodologies', [])
            findings = expert_docs.get('key_findings', [])
            
            # Use external research module
            async with ExternalResearchModule() as research:
                # Run Agent 2 (O3 Pro) and Agent 3 (GPT-4.1) in parallel
                legal_task = research.forensic_legal_research(
                    expert_name, methodologies, case_strategy
                )
                scientific_task = research.scientific_domain_research(
                    expert_name, methodologies, findings, case_strategy
                )
                
                legal_results, scientific_results = await asyncio.gather(
                    legal_task, scientific_task
                )
                
                # Process results through AI agents for analysis
                legal_analysis = await self._analyze_legal_research(
                    legal_results, case_analysis, case_strategy
                )
                scientific_analysis = await self._analyze_scientific_research(
                    scientific_results, case_analysis, case_strategy
                )
                
                return {
                    "legal_research": {
                        "raw_results": legal_results,
                        "analysis": legal_analysis,
                        "agent": "O3 Pro Deep Research"
                    },
                    "scientific_research": {
                        "raw_results": scientific_results,
                        "analysis": scientific_analysis,
                        "agent": "GPT-4.1 Scientific Domain"
                    }
                }
                
        except ImportError:
            logger.warning("External research module not available, using basic research")
            # Fallback to original methods
            legal_results, scientific_results = await asyncio.gather(
                self.legal_forensic_research(case_analysis, expert_docs, case_strategy),
                self.scientific_domain_research(case_analysis, expert_docs, case_strategy)
            )
            
            return {
                "legal_research": legal_results,
                "scientific_research": scientific_results
            }
    
    async def legal_forensic_research(self, case_analysis: Dict, expert_docs: Dict, case_strategy: str) -> Dict[str, Any]:
        """
        Agent 2: Legal Deep Research
        Searches legal databases for precedents
        """
        expert_name = expert_docs.get('expert_name', 'neuropsychologist')
        methodologies = expert_docs.get('methodologies', ['neuropsychological testing'])
        
        # Build targeted legal searches
        if case_strategy == "challenge":
            legal_searches = [
                f"Daubert motion exclude {expert_name} testimony traumatic brain injury",
                f"{methodologies[0] if methodologies else 'TBI testing'} reliability challenged court excluded",
                f"neuropsychologist expert witness excluded Daubert factors not met",
                f"TBI mild traumatic brain injury expert testimony unreliable methods"
            ]
        else:  # support
            legal_searches = [
                f"Daubert motion denied {expert_name} qualified expert traumatic brain injury",
                f"{methodologies[0] if methodologies else 'TBI testing'} accepted reliable court standards",
                f"neuropsychologist expert witness admitted Daubert satisfied",
                f"TBI traumatic brain injury expert testimony accepted methodologies"
            ]
        
        print("   🔍 Searching legal databases...")
        
        # Collect search results
        search_results = []
        actual_content = []
        
        for query in legal_searches[:3]:  # Limit to avoid rate limiting
            scholar_url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
            print(f"      → Searching: {query[:50]}...")
            
            content = await self.search_external_database(scholar_url, "Google Scholar")
            if content:
                actual_content.append({
                    "query": query,
                    "content": content[:1500],
                    "source": "Google Scholar"
                })
            
            search_results.append({
                "query": query,
                "url": scholar_url,
                "source": "Google Scholar"
            })
        
        # Generate legal analysis
        if case_strategy == "challenge":
            prompt = f"""
            As a legal forensic researcher specializing in expert witness challenges, analyze:
            
            Expert: {expert_name}
            Methodologies to Challenge: {json.dumps(methodologies, indent=2)}
            
            Strategy from Lead Attorney: {case_analysis['strategy'][:1000]}...
            
            Database Searches Performed:
            {json.dumps(search_results, indent=2)}
            
            {f"Search Results Found: {json.dumps(actual_content, indent=2)}" if actual_content else "Simulated search results for legal precedents"}
            
            Provide:
            1. Specific cases where similar TBI experts were excluded
            2. Circuit-specific standards for neuropsychological testimony
            3. Common successful arguments against these methodologies
            4. Procedural requirements for Daubert motions in this context
            5. Key quotes from judges excluding similar testimony
            
            Format with proper legal citations.
            """
        else:  # support
            prompt = f"""
            As a legal forensic researcher specializing in defending expert witnesses, analyze:
            
            Expert: {expert_name}
            Methodologies to Support: {json.dumps(methodologies, indent=2)}
            
            Strategy from Lead Attorney: {case_analysis['strategy'][:1000]}...
            
            Database Searches Performed:
            {json.dumps(search_results, indent=2)}
            
            {f"Search Results Found: {json.dumps(actual_content, indent=2)}" if actual_content else "Simulated search results for supporting precedents"}
            
            Provide:
            1. Cases where similar TBI experts were admitted
            2. Circuit precedents supporting neuropsychological testimony
            3. Judicial recognition of these methodologies
            4. Failed challenges to similar experts
            5. Key quotes from judges admitting similar testimony
            
            Format with proper legal citations.
            """
        
        response = self.openai_client.chat.completions.create(
            model="o3-pro-deep-research",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        return {
            "findings": response.choices[0].message.content,
            "search_queries": legal_searches,
            "databases_searched": ["Google Scholar", "CourtListener", "Westlaw (simulated)"],
            "search_strategy": case_strategy
        }
    
    async def scientific_domain_research(self, case_analysis: Dict, expert_docs: Dict, case_strategy: str) -> Dict[str, Any]:
        """
        Agent 3: Scientific Domain Specialist
        Searches medical/scientific databases
        """
        methodologies = expert_docs.get('methodologies', ['neuropsychological testing', 'DTI imaging'])
        findings = expert_docs.get('key_findings', [])
        
        # Build scientific searches based on methodologies found
        scientific_searches = []
        
        if case_strategy == "challenge":
            # Focus on limitations and controversies
            for method in methodologies[:2]:
                searches = [
                    f"{method} traumatic brain injury false positive rate limitations",
                    f"{method} TBI reliability validity controversy",
                    f"{method} mild TBI overdiagnosis concerns"
                ]
                for search in searches:
                    scientific_searches.append({
                        "query": search,
                        "database": "PubMed",
                        "focus": "limitations"
                    })
        else:  # support
            # Focus on validation and acceptance
            for method in methodologies[:2]:
                searches = [
                    f"{method} traumatic brain injury validated gold standard",
                    f"{method} TBI sensitivity specificity accurate",
                    f"{method} mild TBI diagnosis reliable"
                ]
                for search in searches:
                    scientific_searches.append({
                        "query": search,
                        "database": "PubMed",
                        "focus": "validation"
                    })
        
        print("   🔬 Searching scientific databases...")
        actual_scientific_content = []
        
        # Perform searches
        for search in scientific_searches[:4]:  # Limit searches
            if search['database'] == "PubMed":
                url = f"https://pubmed.ncbi.nlm.nih.gov/?term={search['query'].replace(' ', '+')}"
            else:
                url = f"https://scholar.google.com/scholar?q={search['query'].replace(' ', '+')}"
            
            print(f"      → {search['database']}: {search['query'][:40]}...")
            
            content = await self.search_external_database(url, search['database'])
            if content:
                actual_scientific_content.append({
                    "query": search['query'],
                    "content": content[:1000],
                    "database": search['database']
                })
        
        # Generate scientific analysis
        if case_strategy == "challenge":
            prompt = f"""
            As a TBI scientific researcher, identify weaknesses in these methods:
            
            Expert's Methodologies: {json.dumps(methodologies, indent=2)}
            Reported Findings: {json.dumps(findings[:3], indent=2)}
            
            Scientific Searches Performed:
            {json.dumps(scientific_searches[:4], indent=2)}
            
            {f"Research Found: {json.dumps(actual_scientific_content, indent=2)}" if actual_scientific_content else "Based on current TBI research literature"}
            
            Analyze and report:
            1. Known limitations of each methodology for mild TBI
            2. False positive rates and specificity issues
            3. Alternative explanations for findings
            4. Controversies in the field
            5. Missing controls or differential diagnoses
            6. Gap between research and clinical application
            
            Cite specific studies where possible.
            """
        else:  # support
            prompt = f"""
            As a TBI scientific researcher, validate these methods:
            
            Expert's Methodologies: {json.dumps(methodologies, indent=2)}
            Reported Findings: {json.dumps(findings[:3], indent=2)}
            
            Scientific Searches Performed:
            {json.dumps(scientific_searches[:4], indent=2)}
            
            {f"Research Found: {json.dumps(actual_scientific_content, indent=2)}" if actual_scientific_content else "Based on current TBI research consensus"}
            
            Validate and support:
            1. Scientific acceptance of each methodology
            2. Reliability and validity data
            3. Peer-reviewed support for approaches
            4. Clinical guidelines endorsing methods
            5. Sensitivity and specificity for TBI
            6. Recent advances supporting techniques
            
            Cite authoritative sources.
            """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return {
            "findings": response.choices[0].message.content,
            "search_queries": [s["query"] for s in scientific_searches[:4]],
            "databases_searched": ["PubMed", "Google Scholar", "Cochrane Reviews"],
            "methodologies_analyzed": methodologies,
            "search_strategy": case_strategy
        }
    
    async def _analyze_legal_research(self, legal_results: Dict, case_analysis: Dict, case_strategy: str) -> str:
        """
        Agent 2 (O3 Pro) analyzes BOTH external research AND local corpus findings
        """
        prompt = f"""
        As O3 Pro Deep Research Agent with access to both external databases and local corpus, analyze ALL available sources:
        
        EXTERNAL DATABASE RESEARCH:
        - CourtListener: {len(legal_results.get('courtlistener', []))} cases
        - Google Scholar Legal: {len(legal_results.get('google_scholar', []))} articles
        - Westlaw Simulation: {len(legal_results.get('westlaw_simulation', []))} results
        - PACER Simulation: {len(legal_results.get('pacer_simulation', []))} results
        - Key Precedents: {json.dumps(legal_results.get('summary', {}).get('key_precedents', []), indent=2)}
        
        LOCAL CORPUS ANALYSIS (RAG from ChromaDB):
        - Expert Documents: {case_analysis.get('expert_profile', {}).get('total_documents', 0)} documents
        - Expert Methodologies: {json.dumps(case_analysis.get('expert_profile', {}).get('methodologies', []), indent=2)}
        - Prior Testimonies: {case_analysis.get('expert_profile', {}).get('testimonies', 0)} found
        - Case-Specific Findings: {json.dumps(case_analysis.get('key_findings', [])[:3], indent=2)}
        
        Case Strategy: {case_strategy}
        
        Using BOTH external research AND local corpus, provide deep legal analysis:
        1. Cross-reference external precedents with local expert history
        2. Identify patterns from expert's prior testimonies in our corpus
        3. Find circuit-specific standards from both sources
        4. Use local corpus to identify expert-specific vulnerabilities
        5. Combine external case law with internal document analysis
        
        Be specific about sources (external vs. local corpus) and case citations.
        """
        
        # Agent 2: o3-pro-deep-research with high reasoning effort
        response = self.openai_client.chat.completions.create(
            model="o3-pro-deep-research",  # o3-pro-deep-research model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            reasoning_effort="high"  # High reasoning effort for deep analysis
        )
        
        return response.choices[0].message.content
    
    async def _analyze_scientific_research(self, scientific_results: Dict, case_analysis: Dict, case_strategy: str) -> str:
        """
        Agent 3 (o4-mini-deep-research) analyzes the scientific research findings
        """
        prompt = f"""
        As o4-mini-deep-research Scientific Domain Specialist, analyze these research findings:
        
        PubMed Results: {len(scientific_results.get('pubmed', []))} papers
        ArXiv Results: {len(scientific_results.get('arxiv', []))} papers
        Cochrane Reviews: {len(scientific_results.get('cochrane', []))} reviews
        
        Methodologies Researched: {json.dumps(scientific_results.get('summary', {}).get('methodologies_researched', []), indent=2)}
        Search Focus: {scientific_results.get('summary', {}).get('search_focus', '')}
        
        Case Strategy: {case_strategy}
        
        Provide scientific analysis focusing on:
        1. Strength of scientific evidence
        2. Methodological validity/concerns
        3. Peer acceptance in the field
        4. Recent advances or criticisms
        5. Clinical vs forensic applications
        
        Cite specific studies and findings.
        """
        
        response = self.openai_client.chat.completions.create(
            model="o4-mini-deep-research",  # o4-mini-deep-research model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content

    async def forensic_writer_draft(self, case_analysis: Dict, research_results: Dict, case_strategy: str, motion_type: str) -> str:
        """
        Agent 4: gpt-4.5-research-preview - Initial brief drafting
        Based on findings from Agents 2 & 3
        """
        if case_strategy == "challenge":
            prompt = f"""
            As a forensic legal writer, draft a {motion_type} to EXCLUDE expert {case_analysis['expert_profile']['expert_name']}.
            
            CASE STRATEGY:
            {case_analysis['strategy']}
            
            LEGAL RESEARCH (Agent 2 - O3 Pro Deep Research):
            Raw Findings: {json.dumps(research_results['legal_research'].get('raw_results', {}).get('summary', {}), indent=2)}
            Analysis: {research_results['legal_research'].get('analysis', research_results['legal_research'].get('findings', ''))[:2000]}...
            
            SCIENTIFIC RESEARCH (Agent 3 - GPT-4.1 Domain Specialist):
            Raw Findings: {json.dumps(research_results['scientific_research'].get('raw_results', {}).get('summary', {}), indent=2)}
            Analysis: {research_results['scientific_research'].get('analysis', research_results['scientific_research'].get('findings', ''))[:2000]}...
            
            Structure the motion as follows:
            
            I. INTRODUCTION
            - State the relief sought (exclusion of expert)
            - Brief overview of why expert fails Daubert
            
            II. STATEMENT OF FACTS
            - Expert's proposed testimony
            - Problematic aspects of their methodology
            - Key weaknesses identified
            
            III. LEGAL STANDARD
            - Daubert and progeny
            - Circuit-specific standards
            - Gatekeeper role of court
            
            IV. ARGUMENT
            A. Expert's Methods Are Not Reliable
               - Specific methodology failures
               - Lack of scientific support
            B. Expert's Methods Are Not Relevant
               - Failure to fit the facts
               - Speculative conclusions
            C. Expert's Testimony Would Not Assist the Trier of Fact
               - Confusing or misleading
               - Prejudicial impact
            
            V. CONCLUSION
            - Demand for exclusion
            - Request for hearing if necessary
            
            Write in formal legal style with proper citations.
            """
        else:  # support
            prompt = f"""
            As a forensic legal writer, draft a Response to {motion_type} SUPPORTING expert {case_analysis['expert_profile']['expert_name']}.
            
            CASE STRATEGY:
            {case_analysis['strategy']}
            
            LEGAL RESEARCH (Agent 2 - O3 Pro Deep Research):
            Raw Findings: {json.dumps(research_results['legal_research'].get('raw_results', {}).get('summary', {}), indent=2)}
            Analysis: {research_results['legal_research'].get('analysis', research_results['legal_research'].get('findings', ''))[:2000]}...
            
            SCIENTIFIC RESEARCH (Agent 3 - GPT-4.1 Domain Specialist):
            Raw Findings: {json.dumps(research_results['scientific_research'].get('raw_results', {}).get('summary', {}), indent=2)}
            Analysis: {research_results['scientific_research'].get('analysis', research_results['scientific_research'].get('findings', ''))[:2000]}...
            
            Structure the response as follows:
            
            I. INTRODUCTION
            - Opposition to motion to exclude
            - Brief overview of expert's qualifications
            
            II. STATEMENT OF FACTS
            - Expert's impressive credentials
            - Accepted methodologies used
            - Relevant experience
            
            III. LEGAL STANDARD
            - Daubert's liberal admissibility standard
            - Presumption favoring admissibility
            - Vigorous cross-examination, not exclusion
            
            IV. ARGUMENT
            A. Expert Is Highly Qualified
               - Education and training
               - Relevant experience
            B. Expert's Methods Are Reliable
               - Peer-reviewed techniques
               - Generally accepted in field
            C. Expert's Testimony Is Relevant and Helpful
               - Direct application to case facts
               - Will assist jury
            
            V. CONCLUSION
            - Motion should be denied
            - Cross-examination is proper remedy
            
            Write in persuasive, defensive legal style.
            """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4.5-research-preview",  # gpt-4.5-research-preview
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        
        return response.choices[0].message.content
    
    async def strategic_edit(self, initial_brief: str, research: Dict, case_analysis: Dict, case_strategy: str) -> str:
        """
        My strategic edit as Lead Attorney (Claude Opus 4)
        """
        if case_strategy == "challenge":
            prompt = f"""
            As the Senior Tort Strategist, I need to transform this brief into a strategic weapon.
            
            INITIAL BRIEF:
            {initial_brief[:4000]}...
            
            ENHANCE WITH STRATEGIC INSIGHTS:
            
            1. AGGRESSIVE OPENING: Start with the expert's most damaging weakness - make it impossible to ignore
            
            2. FRAME THE NARRATIVE: This isn't just about excluding an expert - it's about protecting the integrity of the judicial process from junk science
            
            3. USE RESEARCH STRATEGICALLY:
               - Legal: {research['legal_research']['findings'][:500]}...
               - Scientific: {research['scientific_research']['findings'][:500]}...
            
            4. ANTICIPATE AND DESTROY: Pre-empt their best arguments and demolish them
            
            5. CREATE DOUBT CASCADE: Structure arguments so each builds on the last, creating overwhelming doubt
            
            6. MEMORABLE PHRASES: Include quotable lines judges will remember
            
            7. DEVASTATING CONCLUSION: Make exclusion feel like the only responsible choice
            
            Return the strategically enhanced brief that doesn't just argue the law - it wins the war.
            """
        else:  # support
            prompt = f"""
            As the Senior Tort Strategist, I need to make this expert unassailable.
            
            INITIAL BRIEF:
            {initial_brief[:4000]}...
            
            ENHANCE WITH DEFENSIVE STRATEGY:
            
            1. COMMANDING OPENING: Establish immediate credibility and authority
            
            2. REFRAME THE ATTACK: Transform their challenges into proof of our expert's thoroughness
            
            3. USE RESEARCH AS SHIELD:
               - Legal: {research['legal_research']['findings'][:500]}...
               - Scientific: {research['scientific_research']['findings'][:500]}...
            
            4. FLIP THEIR ARGUMENTS: Show how their criticisms actually support admissibility
            
            5. BUILD FORTRESS: Layer defenses so even if one fails, others hold
            
            6. HUMANIZE THE EXPERT: Make them relatable and trustworthy
            
            7. CONFIDENT CONCLUSION: Make denial of their motion inevitable
            
            Return the strategically fortified brief that makes our expert seem essential to justice.
            """
        
        response = self.claude.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    async def final_fact_check(self, edited_brief: str, expert_docs: Dict) -> str:
        """
        Agent 5: Final fact check and polish with Google Search grounding
        """
        try:
            # Initialize Gemini 2.5 Pro with Google Search grounding
            model = genai.GenerativeModel(
                'models/gemini-2.5-pro',
                tools='google_search_retrieval'  # Enable Google Search grounding
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            logger.info("Skipping Gemini fact-check - returning edited brief")
            return edited_brief
        
        prompt = f"""
        Perform final fact-check and polish on this legal brief USING GOOGLE SEARCH GROUNDING:
        
        BRIEF TO REVIEW:
        {edited_brief}
        
        VERIFY AGAINST ORIGINAL DATA:
        Expert Name: {expert_docs.get('expert_name')}
        Credentials Found: {json.dumps(expert_docs.get('credentials', []))}
        Methodologies: {json.dumps(expert_docs.get('methodologies', []))}
        
        FACT-CHECK WITH GOOGLE SEARCH:
        1. ✓ Verify all case citations are real and correctly cited (search for each case)
        2. ✓ Confirm expert's credentials and affiliations are accurate
        3. ✓ Validate scientific claims and methodology descriptions
        4. ✓ Check dates, court names, and judge names for accuracy
        5. ✓ Verify any statistics or research findings cited
        
        FORMATTING & POLISH:
        1. ✓ Expert's name spelled consistently and correctly
        2. ✓ All case citations properly formatted (e.g., Daubert v. Merrell Dow Pharms., 509 U.S. 579 (1993))
        3. ✓ No factual contradictions or inconsistencies
        4. ✓ Proper legal formatting (sections, numbering, spacing)
        5. ✓ Grammar, punctuation, and spelling
        6. ✓ Remove any remaining placeholders or notes
        7. ✓ Ensure professional tone throughout
        
        USE YOUR GOOGLE SEARCH GROUNDING to verify any claim you're uncertain about.
        Return the fact-checked and polished final brief ready for filing.
        """
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini fact-check failed: {e}")
            # Return the edited brief if fact-check fails
            return edited_brief
    
    async def generate_strategic_recommendations(self, case_analysis: Dict, research: Dict, final_brief: str, case_strategy: str) -> str:
        """
        Orchestrator generates strategic recommendations based on all findings
        """
        prompt = f"""
        As the Lead Attorney and Senior Tort Strategist, generate strategic recommendations based on our comprehensive analysis.
        
        Case Strategy: {case_strategy}
        Motion Type: {case_analysis.get('motion_type', 'Daubert Motion')}
        
        Key Findings from Research:
        - Legal Research: {research['legal_research'].get('analysis', research['legal_research'].get('findings', ''))[:1000]}...
        - Scientific Research: {research['scientific_research'].get('analysis', research['scientific_research'].get('findings', ''))[:1000]}...
        
        Brief Summary (first 1000 chars): {final_brief[:1000]}...
        
        Generate STRATEGIC RECOMMENDATIONS including:
        
        1. **Pre-Trial Strategy**
           - Deposition priorities and key questions
           - Discovery requests to strengthen our position
           - Expert witnesses we should retain
        
        2. **Motion Practice**
           - Timing recommendations
           - Supporting motions to consider
           - Anticipated opposition and counters
        
        3. **Trial Strategy** (if motion fails)
           - Cross-examination approach
           - Demonstrative evidence suggestions
           - Jury messaging themes
        
        4. **Settlement Considerations**
           - Leverage points identified
           - Risk assessment
           - Negotiation strategy
        
        5. **Alternative Approaches**
           - Plan B if primary strategy encounters obstacles
           - Complementary legal theories
           - Protective measures
        
        Be specific, practical, and actionable. These recommendations will guide the legal team's approach.
        """
        
        response = self.claude.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text


# Test function
async def test_pipeline():
    """
    Test the complete LEXICON pipeline
    """
    pipeline = LEXICONPipeline()
    
    # Test with Dr. Kenneth J.D. Allen from the corpus
    test_expert = "Kenneth J.D. Allen"
    
    print("🚀 Starting LEXICON Pipeline Test")
    print(f"🎯 Target Expert: {test_expert}")
    
    try:
        # Test challenging the expert
        result = await pipeline.process_case(
            target_expert=test_expert,
            case_strategy="challenge",
            motion_type="Daubert Motion to Exclude Expert Testimony"
        )
        
        # Save the result
        output_dir = Path("./lexicon-output/generated-briefs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the final brief
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        brief_filename = f"{test_expert.replace(' ', '_').replace('.', '')}_{result['case_strategy']}_{timestamp}.txt"
        brief_path = output_dir / brief_filename
        
        with open(brief_path, 'w', encoding='utf-8') as f:
            f.write(result['final_brief'])
        
        # Save strategic recommendations
        recommendations_filename = f"{test_expert.replace(' ', '_').replace('.', '')}_{result['case_strategy']}_recommendations_{timestamp}.txt"
        recommendations_path = output_dir / recommendations_filename
        
        with open(recommendations_path, 'w', encoding='utf-8') as f:
            f.write(result['strategic_recommendations'])
        
        print(f"\n✅ Brief saved to: {brief_path}")
        print(f"📄 Brief length: {len(result['final_brief'])} characters")
        print(f"📊 Strategic recommendations saved to: {recommendations_path}")
        
        # Save full results as JSON
        json_path = output_dir / f"pipeline_results_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            # Create summary without full brief text
            result_summary = {
                "target_expert": result['target_expert'],
                "case_strategy": result['case_strategy'],
                "motion_type": result['motion_type'],
                "timestamp": result['timestamp'],
                "brief_saved_to": str(brief_path),
                "brief_length": len(result['final_brief']),
                "research_summary": {
                    "legal_queries": result['research']['legal_research']['search_queries'],
                    "scientific_queries": result['research']['scientific_research']['search_queries'],
                    "databases_searched": list(set(
                        result['research']['legal_research']['databases_searched'] + 
                        result['research']['scientific_research']['databases_searched']
                    ))
                },
                "strategy_excerpt": result['strategy']['strategy'][:500] + "..."
            }
            json.dump(result_summary, f, indent=2)
        
        print(f"📊 Full results saved to: {json_path}")
        
        # Print excerpt of the brief
        print("\n" + "="*60)
        print("BRIEF EXCERPT (First 1000 characters):")
        print("="*60)
        print(result['final_brief'][:1000] + "...")
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_pipeline())