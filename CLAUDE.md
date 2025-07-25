# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LEXICON** is an AI-powered legal research and brief writing system for a tort law firm potential client (Allen Law Group), focused om traumatic brain injury (TBI) cases for MVP/demo purposes. It uses a multi-agent (latest versions of 5 state-of-the-art models from diffrent providers) RAG architecture (with multiple MCP servers) to analyze expert witness testimony, searching relevant medical literature annd legal precedents to generate strategic legal briefs. Specifically, the 5-agent workflow comprises: **1. Orchestrator: Claude Opus 4**, who will (a) anonymize and parse user-uploaded legal documents, plaintiff medical records, depositions, and export reports; once complete, these will be stored locally; (b) Opus 4 will generate a case file summary (informed by their user-uploade document review) to pass to the researchers, who will work concurrently and communicate with one another during the search-and-retrieval process; **2. Legal Researcher: o3-pro-deep-research**, who will (a) summarize and/or quote relevant caselaw precedent germane to the case and/or expert witnesses using available internal (i.e., user-uploaded files, corpus of former briefs) and external databases (e.g., Google Scholar (case law filter), CourtWhisperer); concurrently, the **3. Scientific Researcher: o4-mini-deep-research**, will similarly (a) access, (b) retrieve, and (c) integrate (from internal documents and available external databases) to generate output into an empirically-supported unified narrative summary report with accurate and contemporary publication citations from reputable peer-reviewed academic journals, while also (e) storing domain-knowledge that might be helpful for similar cases. Once each agent has compiled their summary reports, the **Orchestrator** will review their work for accuracy and completeness: specifically, as the **Orchestrator**, Claude Opus 4 will be responsible for: (a) querying eeach model as necessary for clarification, (b) asking for revisions if needed, and once complete, (C) passing the narrative file to the fourth agent; **4.Brief Writer**, who will use this summary to inform their selection of recommmend proven legal strategies to include with the brief, in addition to generating the first draft of the final brief requested by the user before passing the initial draft back to the **Orchestrator**, who wiil (a) clarify and revise as necessary before passing the revised draft to the final agent; **5. Editor: Gemini 2.5 Pro** (chosen for its long context window and grounding capabilities using Google services), who will (a) ensure the accuracy and relevance of all cited material, (b) correct any typological errors detected, and (c) format the document according to the latest edition of MLA style and the client firm's internal templates. Finally, **LEXICON** will output a full legal brief (as the user originally requested) with correct citations (triple-checked for accuracy) and a seperate fine strategic recommendations for the present case based on the agents' findings. The current version is an MVP (in the alpha development stage) with limited capabilities (Daubert exclusion for defendant expert witnesses) and scope (TBI cases) to demonstrate proof-of-concept. The MVP will draw from a curated subset of documents (from the client firm, largely comprising motions *in limine*, including Daubert/Frye exclusions, opposition to such motions to exclude evidence, responses to defendant motions, expert reports, CVs, depositions, judgment orders, etc.) from the larger corpus of 6000+ files. There are additionally legal documents and expert witness reports drawn from other pertinent litigation. While most of the available documents are not TBI-related, this alpha testing will demonstrate LEXICON's flexibility, semantic comprehension, and ability to identify relevant information embedded in big datasets.

## Essential Command

### Backend Development
```bash
# Install dependencies
pip install -r requirements_complete.txt

# Run main applications
python lexicon_complete_package.py  # Interactive menu system
python lexicon_webapp.py            # Web interface (Flask + Socket.IO)
python lexicon_pipeline.py          # Direct pipeline access

# Document processing
python document_processor.py        # Process new documents
python convert_wpd_files.py         # Convert WordPerfect files

# Run tests
python test_lexicon_pipeline.py     # Pipeline integration tests
python test_tbi_daubert_search.py   # Search functionality tests
```

### Frontend Development
```bash
cd frontend
npm install                         # Install dependencies
npm start                           # Development server (port 3000)
npm run build                       # Production build
npm test                            # Run tests
```

### Docker Development
```bash
# Development environment (ChromaDB + Redis)
docker-compose up -d

# Full multi-agent production setup
docker-compose -f docker-compose-full.yml up -d
```

## Architecture Overview

### Multi-Agent Pipeline
The system uses a 5-agent architecture with state-of-the-art models:

1. **Orchestrator** (`docker/agent-orchestrator/`): Claude Opus 4
   - Anonymizes and parses uploaded documents (medical records, depositions, expert reports)
   - Generates case file summaries for researcher agents
   - Coordinates workflow and reviews agent outputs
   - Queries agents for clarification and requests revisions

2. **Legal Research Agent** (`docker/agent-legal-research/`): o3-pro-deep-research
   - Searches internal corpus (user uploads, prior briefs)
   - Queries external databases (Google Scholar with case law filter, CourtWhisperer)
   - Summarizes and quotes relevant caselaw precedents
   - Focuses on Daubert/Frye exclusions and expert witness challenges

3. **Scientific Research Agent** (`docker/agent-scientific-research/`): o4-mini-deep-research
   - Retrieves peer-reviewed medical literature
   - Integrates findings from internal and external sources
   - Generates empirically-supported narrative summaries
   - Stores domain knowledge for future cases

4. **Brief Writer Agent** (`docker/agent-writer/`): gpt-4.5-research-preview
   - Synthesizes research summaries from both researchers
   - Selects proven legal strategies based on findings
   - Generates first draft of legal brief
   - Returns draft to Orchestrator for review

5. **Editor Agent** (`docker/agent-editor/`): Gemini 2.5 Pro
   - Verifies accuracy of all citations
   - Corrects typographical errors
   - Formats according to MLA style and firm templates
   - Leverages long context window for comprehensive review

### Core Components
- **Vector Database**: ChromaDB stores 8,505+ legal document embeddings
- **Cache Layer**: Redis for session management and real-time updates
- **API Gateway**: Nginx routes requests to appropriate agents
- **WebSocket**: Real-time progress updates via Socket.IO

### Data Flow
1. User uploads documents (expert testimony, medical records, depositions) → `uploads/`
2. Orchestrator (Claude Opus 4) anonymizes and parses documents
3. Orchestrator generates case file summary for researcher agents
4. Legal & Scientific Researchers work concurrently:
   - Search internal corpus and vector database
   - Query external databases (Google Scholar, PubMed, etc.)
   - Compile research summaries
5. Orchestrator reviews research, requests clarifications/revisions
6. Brief Writer synthesizes findings into first draft
7. Orchestrator reviews and refines draft
8. Editor (Gemini 2.5 Pro) polishes and formats final brief
9. System outputs:
   - Full legal brief with verified citations → `generated-briefs/`
   - Strategic recommendations document

## API Configuration

Required environment variables in `.env`:
```
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
GOOGLE_API_KEY=your_key  # or GOOGLEAI_STUDIO_API_KEY
FIRECRAWL_API_KEY=your_key  # optional
COURTLISTENER_API_KEY=your_key  # optional
```

## MCP Server Configuration

The system uses Model Context Protocol (MCP) servers for enhanced capabilities:

### Available MCP Servers (from mcp-config.json):
- **Filesystem**: Secure file operations with allowed/blocked directory controls
- **Memory**: Persistent context storage across sessions
- **Fetch**: Web content retrieval and processing
- **GitHub**: Repository integration and code search

### MCP Features:
- Document anonymization and parsing
- Inter-agent communication channels
- External database connectivity (Google Scholar, CourtWhisperer)
- Session state persistence
- Real-time collaboration between researcher agents

## Key Files and Directories

### Backend Logic
- `lexicon_pipeline.py`: Core pipeline orchestration
- `document_processor.py`: Document ingestion and vectorization
- `lexicon_webapp.py`: Flask web server with Socket.IO
- `tbi_daubert_search.py`: Legal precedent search functionality

### Frontend Structure
- `frontend/src/components/`: React components (FileUpload, Results, etc.)
- `frontend/src/services/api.ts`: Backend API integration
- `frontend/src/types/`: TypeScript type definitions

### Document Corpus
- `tbi-corpus/raw/`: Original legal documents
- `tbi-corpus/processed/`: Extracted text and metadata
- `vector_store/`: ChromaDB persistent storage

## Testing Strategy

Run tests before commits:
```bash
# Backend tests
python test_lexicon_pipeline.py
python test_tbi_daubert_search.py
python test_api_config.py

# Frontend tests
cd frontend && npm test
```

## Development Tips

1. **Vector Database**: Ensure ChromaDB is running before starting the application
2. **API Keys**: Verify all required API keys are configured in `.env`
3. **Document Processing**: Use `document_processor.py` for batch processing new documents
4. **Real-time Updates**: WebSocket events are emitted during pipeline execution for UI updates
5. **Multi-Agent Mode**: Use `docker-compose-full.yml` for production-like testing

## Common Issues

1. **ChromaDB Connection**: Ensure Docker container is running: `docker-compose up -d chroma`
2. **WordPerfect Files**: Use `convert_wpd_files.py` with LibreOffice installed
3. **API Rate Limits**: Implement retry logic for external API calls
4. **Memory Usage**: Large document batches may require increased Docker memory limits