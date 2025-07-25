# LEXICON Complete Package Setup Guide

## 🏛️ Overview

LEXICON is a comprehensive legal AI system that combines:
- **Document Preprocessing**: Extract text, generate metadata, create vector embeddings
- **WordPerfect Conversion**: Convert legacy .wpd files to PDF
- **AI Pipeline**: Generate strategic legal briefs using multiple AI agents
- **Neutral Strategy**: Support OR challenge expert witnesses based on your needs

## 📋 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- Docker Desktop (for ChromaDB)
- LibreOffice (for WordPerfect conversion)
- API Keys (Anthropic, OpenAI, Google AI)

### 2. Installation

```bash
# Clone or navigate to the directory
cd C:\Users\jdall\lexicon-mvp-alpha

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements_pipeline.txt

# Or install manually
pip install anthropic openai google-generativeai chromadb PyPDF2 python-docx pypandoc langchain python-dotenv requests aiohttp
```

### 3. Environment Setup

Create a `.env` file with your API keys:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-google-ai-key
FIRECRAWL_API_KEY=your-firecrawl-key  # Optional for web scraping
```

### 4. Start ChromaDB

```bash
# Using Docker Compose
docker-compose up -d

# Or run ChromaDB directly
docker run -d -p 8000:8000 chromadb/chroma
```

### 5. Install LibreOffice (for WordPerfect files)

Download from: https://www.libreoffice.org/download/
- Install with default settings
- The system will auto-detect the installation

## 🚀 Using the Complete Package

### Run the All-in-One System

```bash
python lexicon_complete_package.py
```

This provides a menu-driven interface:

```
🏛️  LEXICON COMPLETE LEGAL AI SYSTEM
================================================================================
Unified package for document processing and legal brief generation
================================================================================

🔧 Checking LEXICON environment...
✅ API keys configured
✅ ChromaDB connected
✅ LibreOffice found: C:\Program Files\LibreOffice\program\soffice.exe

📊 Corpus Status: 8505 vectors in database

------------------------------------------------------------
MAIN MENU:
1. Preprocess new documents
2. Search the corpus
3. Generate legal brief (support expert)
4. Generate legal brief (challenge expert)
5. View corpus statistics
6. Exit
------------------------------------------------------------

Select option (1-6): 
```

### Option 1: Preprocess Documents

Processes all documents in your corpus folder:
- Extracts text from PDFs, DOCX, TXT files
- Converts WordPerfect (.wpd) files to PDF
- Uses Claude to extract metadata
- Creates vector embeddings for search

### Option 2: Search the Corpus

Search across all preprocessed documents:
```
Enter search query: DTI imaging traumatic brain injury

Found 15 results:
1. Non-client firm expert nsci AllenPhD-Report3-Arackal.pdf
   DTI assessment performed November 30, 2022 shows evidence of ongoing neurodegeneration...
```

### Option 3: Support Your Expert

Generate a brief defending your expert:
```
SUPPORT EXPERT MODE
Enter expert name: Dr. Kenneth J.D. Allen

Generating brief...
✅ Brief saved to: ./lexicon-output/briefs/support_Dr_Kenneth_JD_Allen_20250722_095423.txt
```

### Option 4: Challenge Opposing Expert

Generate a motion to exclude opposing expert:
```
CHALLENGE EXPERT MODE
Enter expert name: Dr. Defense Expert

Generating brief...
✅ Brief saved to: ./lexicon-output/briefs/challenge_Dr_Defense_Expert_20250722_095623.txt
```

## 📁 Directory Structure

```
lexicon-mvp-alpha/
├── lexicon_complete_package.py    # All-in-one system
├── .env                          # API keys
├── docker-compose.yml            # ChromaDB setup
├── tbi-corpus/                   # Your document corpus
│   ├── processed/               # Original documents
│   └── converted_from_wpd/      # Converted PDFs
└── lexicon-output/              # Generated output
    └── briefs/                  # Legal briefs
```

## 🔧 Advanced Usage

### Programmatic Access

```python
from lexicon_complete_package import LEXICONCompleteSystem
import asyncio

async def example():
    # Initialize system
    system = LEXICONCompleteSystem()
    
    # Search corpus
    results = system.search_corpus("neuropsychological testing reliability")
    
    # Generate support brief
    brief = await system.generate_brief(
        expert_name="Dr. Kenneth J.D. Allen",
        strategy="support",
        motion_type="Response to Daubert Motion"
    )
    
    print(brief['final_brief'])

asyncio.run(example())
```

### Batch Processing

```python
# Process multiple experts
experts_to_support = ["Dr. Allen", "Dr. Richerson"]
experts_to_challenge = ["Dr. Defense Expert 1", "Dr. Defense Expert 2"]

for expert in experts_to_support:
    result = await system.generate_brief(expert, "support")
    # Save brief...

for expert in experts_to_challenge:
    result = await system.generate_brief(expert, "challenge")
    # Save brief...
```

## 🛠️ Troubleshooting

### ChromaDB Connection Error
```bash
# Check if Docker is running
docker ps

# Restart ChromaDB
docker-compose restart chromadb
```

### API Key Issues
- Verify keys in .env file
- Check API credit balance
- Ensure proper formatting (no extra spaces)

### WordPerfect Conversion Fails
- Ensure LibreOffice is installed
- Check file permissions
- Try manual conversion first

### Memory Issues
- Process documents in smaller batches
- Increase Docker memory allocation
- Close other applications

## 📊 System Components

### 1. Document Processor
- Extracts text from multiple formats
- AI-powered metadata extraction
- Creates searchable vector embeddings

### 2. WordPerfect Converter
- Finds all .wpd files
- Converts to PDF using LibreOffice
- Maintains directory structure

### 3. LEXICON Pipeline
- 6-stage AI orchestration
- Parallel legal and scientific research
- Strategic brief generation

### 4. Complete System
- Unified interface
- Environment checking
- Statistics and monitoring

## 🎯 Strategic Capabilities

### Support Mode
- Emphasizes expert qualifications
- Validates methodologies
- Finds supporting precedents
- Builds defensive arguments

### Challenge Mode
- Identifies vulnerabilities
- Questions reliability
- Finds exclusion precedents
- Creates aggressive arguments

## 📈 Performance Tips

1. **Initial Setup**: First preprocessing may take 30-60 minutes
2. **API Usage**: Monitor API costs, especially during batch processing
3. **Search Optimization**: Use specific terms for better results
4. **Brief Generation**: Each brief takes 2-3 minutes to generate

## 🔐 Security Notes

- Keep API keys secure
- Don't commit .env file to version control
- Use read-only access for document folders
- Review generated briefs before filing

## 📞 Support

For issues:
1. Check error messages in console
2. Verify all dependencies installed
3. Ensure services are running
4. Review API quotas

## 🚀 Next Steps

1. Run initial preprocessing of your corpus
2. Test search functionality
3. Generate sample briefs for review
4. Integrate with your workflow
5. Customize prompts for your jurisdiction

---

LEXICON: Balanced, Strategic, Powerful Legal AI