# LEXICON - AI-Powered Legal Research & Brief Writing System

![LEXICON Architecture](LEXICON%20v0.1.5%20Architecture.jpeg)

LEXICON is an advanced AI-powered legal research and brief writing system designed for tort law firms, with a current focus on traumatic brain injury (TBI) cases. It uses a multi-agent RAG (Retrieval-Augmented Generation) architecture with state-of-the-art models from multiple providers to analyze expert witness testimony, search relevant medical literature and legal precedents, and generate strategic legal briefs.

## Key Features

- **Multi-Agent Architecture**: 5 specialized AI agents working in concert
- **Advanced Document Processing**: Handles WordPerfect, PDF, and various document formats
- **Expert Witness Analysis**: Specialized in Daubert/Frye exclusion motions
- **Real-time Collaboration**: WebSocket-based progress tracking
- **Secure Document Handling**: Automatic anonymization and secure storage
- **External Database Integration**: Google Scholar, CourtWhisperer, PubMed
- **MCP Integration**: Model Context Protocol for enhanced agent capabilities

## System Architecture

### AI Agents

1. **Orchestrator** (Claude Opus 4)
   - Document anonymization and parsing
   - Workflow coordination
   - Quality control and revision requests

2. **Legal Research Agent** (o3-pro-deep-research)
   - Caselaw precedent search
   - Daubert/Frye exclusion expertise
   - Internal corpus analysis

3. **Scientific Research Agent** (o4-mini-deep-research)
   - Medical literature retrieval
   - Peer-reviewed journal integration
   - Empirical evidence compilation

4. **Brief Writer** (gpt-4.5-research-preview)
   - Strategic legal brief generation
   - Research synthesis
   - Legal strategy recommendations

5. **Editor** (Gemini 2.5 Pro)
   - Citation verification
   - MLA formatting
   - Final quality assurance

## Quick Start

### Prerequisites

- Docker Desktop
- Python 3.9+
- Node.js 16+
- API keys for: Anthropic, OpenAI, Google AI

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lexicon-mvp-alpha.git
cd lexicon-mvp-alpha
```

2. Copy the environment file and add your API keys:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the quick start script:
```bash
./LEXICON.bat  # Windows
# or
./deploy-local.sh  # Linux/Mac
```

### Development Setup

For detailed setup instructions, see:
- [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)
- [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md)
- [LEXICON_COMPLETE_SETUP.md](LEXICON_COMPLETE_SETUP.md)

## Usage

### Web Interface
```bash
python lexicon_webapp.py
# Open http://localhost:5000
```

### Command Line
```bash
python lexicon_complete_package.py
```

### Docker Deployment
```bash
docker-compose -f docker-compose-full.yml up -d
```

## Documentation

- **Architecture**: [LEXICON_PIPELINE_README.md](LEXICON_PIPELINE_README.md)
- **Web App**: [WEBAPP_README.md](WEBAPP_README.md)
- **Research Integration**: [LEXICON_RESEARCH_INTEGRATION.md](LEXICON_RESEARCH_INTEGRATION.md)
- **External Research**: [EXTERNAL_RESEARCH_README.md](EXTERNAL_RESEARCH_README.md)
- **API Configuration**: [API_KEYS_USAGE.md](API_KEYS_USAGE.md)

## Testing

Run the comprehensive test suite:
```bash
./RUN-COMPREHENSIVE-TEST.bat  # Windows
```

Run pre-flight checks:
```bash
./RUN-PREFLIGHT-CHECK.bat  # Windows
```

## Project Structure

```
lexicon-mvp-alpha/
├── backend/              # Core Python backend
├── frontend/             # React TypeScript frontend
├── docker/               # Docker configurations for agents
├── tbi-corpus/           # Legal document corpus
├── vector_store/         # ChromaDB vector storage
├── templates/            # HTML templates
├── static/               # Static assets
└── generated-briefs/     # Output directory
```

## Security Considerations

- All uploaded documents are automatically anonymized
- API keys are stored in environment variables
- Document access is restricted by agent permissions
- Redis provides secure session management
- See [security best practices](LOCAL_DEPLOYMENT.md#security-considerations)

## Contributing

This is currently an MVP in alpha development. For contributions:

1. Fork the repository
2. Create a feature branch
3. Run tests before committing
4. Submit a pull request

## License

[License information to be added]

## Contact

For questions or support regarding the LEXICON system, please contact the development team.

## Acknowledgments

- Allen Law Group for project sponsorship
- All contributors to the open-source libraries used in this project