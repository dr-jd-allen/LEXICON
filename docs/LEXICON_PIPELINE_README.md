# **LEXICON**: Legal Expertise with Contextual Intelligence - Complete Workflow Implementation

## Overview

LEXICON is a sophisticated AI-powered legal research and brief writing system that orchestrates multiple AI agents to analyze expert witness testimony and other case facts generate strategic legal briefs regarding the admissibility of evidence (e.g., motions *in limine*).

**Important**: LEXICON adheres to a neutral legal strategy tool that can both SUPPORT and CHALLENGE expert witnesses based on user case needs. It's designed to help legal teams develop the strongest possible arguments for their position, whether defending their own experts or challenging opposing experts.

## Key Features

### 1. **Vector Database Search** (Claude Opus 4)** 
- Searches your preprocessed TBI corpus (8,505 vectors)
- Finds all documents related to a specific expert
- Extracts methodologies, credentials, and key findings

### 2. **Strategic Analysis (Claude Opus 4)**
- Develops comprehensive case strategy
- Identifies vulnerabilities (for challenges) or strengths (for support)
- Provides specific Daubert factor analysis

### 3. **Parallel Research**
- **Legal Research Agent**: Searches for relevant case law and precedents
- **Scientific Research Agent**: Investigates methodological validity
- Both agents work simultaneously for efficiency

### 4. **Brief Generation Pipeline**
- **Initial Draft**: Created by forensic legal writer
- **Strategic Enhancement**: Refined by lead attorney AI
- **Final Polish**: Fact-checked and formatted

## Setup

1. **Install Dependencies**:
```bash
pip install -r requirements_pipeline.txt
```

2. **Environment Variables** (.env file):
```
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_ai_key
FIRECRAWL_API_KEY=your_firecrawl_key  # Optional
```

3. **Ensure ChromaDB is Running**:
```bash
docker-compose up -d
```

## Strategic Use Cases

### For Plaintiff's Counsel
- **SUPPORT** your medical experts against Daubert challenges
- **CHALLENGE** defense experts who minimize injuries
- Generate responses to motions to exclude
- Build affirmative motions to qualify experts

### For Defense Counsel  
- **SUPPORT** your experts' alternative explanations
- **CHALLENGE** plaintiff's causation experts
- Generate Daubert motions to exclude
- Defend against qualification challenges

## Usage

### Supporting Your Expert

```python
from lexicon_pipeline import LEXICONPipeline
import asyncio

async def support_our_expert():
    pipeline = LEXICONPipeline()
    
    # Defend our expert against a Daubert challenge
    result = await pipeline.process_case(
        target_expert="Dr. Kenneth J.D. Allen",
        case_strategy="support",
        motion_type="Response to Defendant's Daubert Motion"
    )
    
    print(result['final_brief'])

asyncio.run(support_our_expert())
```

### Challenging Opposing Expert

```python
async def challenge_their_expert():
    pipeline = LEXICONPipeline()
    
    # Challenge opposing expert
    result = await pipeline.process_case(
        target_expert="Dr. Defense Expert",
        case_strategy="challenge",
        motion_type="Daubert Motion to Exclude"
    )
    
    print(result['final_brief'])

asyncio.run(challenge_their_expert())
```

### Test the Pipeline

```bash
python lexicon_pipeline.py
```

This will:
1. Search for documents about Dr. Kenneth J.D. Allen
2. Develop a strategy to challenge his testimony
3. Research legal precedents and scientific literature
4. Generate a complete Daubert motion
5. Save the brief to `./lexicon-output/generated-briefs/`

## Pipeline Stages

### Stage 1: Document Search
- Searches ChromaDB for expert-related documents
- Extracts credentials, methodologies, and findings
- Builds comprehensive expert profile

### Stage 2: Strategic Analysis
- Claude Opus 4 acts as Senior Tort Strategist
- Analyzes expert vulnerabilities or strengths
- Develops targeted legal strategy

### Stage 3: Parallel Research
- **Legal Agent**: Searches Google Scholar, CourtListener (simulated)
- **Scientific Agent**: Searches PubMed, ArXiv (simulated)
- Finds supporting evidence for the strategy

### Stage 4: Brief Writing
- Forensic writer creates initial draft
- Follows proper legal structure and citations
- Incorporates research findings

### Stage 5: Strategic Enhancement
- Lead attorney AI enhances persuasiveness
- Adds strategic framing and memorable arguments
- Anticipates opposing arguments

### Stage 6: Final Polish
- Fact-checks all claims
- Ensures consistent formatting
- Verifies legal citations

## Output Files

The pipeline generates:

1. **Legal Brief** (`[expert_name]_[strategy]_[timestamp].txt`)
   - Complete motion ready for review
   - Properly formatted with legal citations
   - Strategic arguments based on research

2. **Pipeline Results** (`pipeline_results_[timestamp].json`)
   - Summary of the process
   - Research queries performed
   - Strategy excerpts
   - File locations

## Customization

### Different Motion Types
```python
# Daubert Motion
motion_type="Daubert Motion to Exclude Expert Testimony"

# Motion in Limine
motion_type="Motion in Limine to Exclude Expert"

# Response to Daubert
motion_type="Response to Defendant's Daubert Motion"
```

### Case Strategies
- `"challenge"`: Generate motion to exclude expert
- `"support"`: Generate response defending expert

### External Database Integration

To enable real web scraping:
1. Get a Firecrawl API key from https://firecrawl.dev
2. Add to .env: `FIRECRAWL_API_KEY=your_key`
3. The pipeline will scrape actual search results

## Current Limitations

1. **Model Availability**:
   - Uses GPT-4 instead of O3 Pro (not yet available)
   - Uses Gemini Pro instead of Gemini 2.5 Pro

2. **External Searches**:
   - Without Firecrawl API, uses simulated search results
   - Real implementation would scrape actual databases

3. **API Rate Limits**:
   - Be mindful of API usage
   - Consider implementing caching for repeated searches

## Future Enhancements

1. **Dify.ai Integration**: Connect to orchestration platform
2. **Real-time Collaboration**: Multiple agents working on sections
3. **Citation Verification**: Automated checking of case citations
4. **Template Library**: Pre-built motion templates
5. **Jurisdiction Customization**: State-specific requirements

## Troubleshooting

### ChromaDB Connection Error
```bash
# Ensure Docker is running
docker ps
# Restart ChromaDB
docker-compose restart chromadb
```

### API Key Issues
- Verify all keys in .env file
- Check API credit balance
- Ensure keys have proper permissions

### Memory Issues
- The pipeline processes large texts
- Ensure adequate RAM (8GB+ recommended)
- Consider batch processing for multiple experts

## Support

For issues or questions:
1. Check the error logs in `lexicon-output/logs/`
2. Verify all dependencies are installed
3. Ensure ChromaDB has the preprocessed corpus

## Next Steps

1. Test with different experts from your corpus
2. Fine-tune prompts for your specific needs
3. Integrate with your law firm's document management
4. Add custom templates for different jurisdictions
5. Implement review workflow for generated briefs