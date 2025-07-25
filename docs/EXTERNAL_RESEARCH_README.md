# LEXICON External Research Module

## Overview

The External Research Module implements real database searches for LEXICON's research agents:
- **Agent 2 (O3 Pro Deep Research)**: Forensic legal research
- **Agent 3 (GPT-4.1 Scientific Domain)**: Scientific and medical research

## Agent Workflow

### 1. Claude Opus 4 (Orchestrator)
- Analyzes expert profile from vector database
- Develops case strategy
- Directs research priorities for Agents 2 & 3

### 2. Agent 2: O3 Pro Deep Research (Legal)
Searches multiple legal databases:
- **CourtListener**: Federal and state case law
- **Google Scholar Legal**: Law review articles, legal precedents
- **Westlaw** (simulated): Comprehensive legal research
- **PACER** (simulated): Federal court documents

### 3. Agent 3: GPT-4.1 Scientific Domain
Searches scientific databases:
- **PubMed**: Medical literature and clinical studies
- **ArXiv**: Cutting-edge research papers
- **Google Scholar Scientific**: Peer-reviewed articles
- **Cochrane Reviews**: Systematic reviews and meta-analyses

### 4. Agent 4: GPT-4.5 Research Preview
- Receives findings from Agents 2 & 3
- Drafts initial legal brief
- Incorporates external research citations

### 5. Claude Opus 4 (Strategic Edit)
- Reviews and enhances the brief
- Adds strategic framing
- Ensures research is used effectively

### 6. Agent 5: Gemini 2.5 Pro
- Final fact-checking
- Verifies citations
- Polishes language

## API Configuration

Add these to your `.env` file:

```env
# Required
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key
GOOGLE_API_KEY=your-key

# Optional - External Research APIs
FIRECRAWL_API_KEY=your-key        # Web scraping
SERP_API_KEY=your-key             # Google Scholar access
PUBMED_API_KEY=your-key           # PubMed E-utilities
COURTLISTENER_API_KEY=your-key    # Case law database
```

## Database Access

### Legal Databases

#### CourtListener (Free API)
- Get API key: https://www.courtlistener.com/api/
- Searches federal and state cases
- Returns case names, citations, excerpts

#### Google Scholar Legal
- Via SERP API or web scraping
- Law review articles
- Case citations and analysis

#### Westlaw/Lexis (Simulated)
- Would require paid subscription
- Currently returns simulated results
- Shows what queries would be run

#### PACER (Simulated)  
- Federal court documents
- Requires credentials
- Currently returns simulated results

### Scientific Databases

#### PubMed
- Free E-utilities API
- Get API key: https://www.ncbi.nlm.nih.gov/account/
- Medical literature search
- Returns titles, authors, abstracts

#### ArXiv
- Free API, no key required
- Preprint research papers
- Physics, math, CS, biology

#### Google Scholar Scientific
- Via SERP API or scraping
- Peer-reviewed papers
- Citation counts

#### Cochrane Reviews
- Currently simulated
- Systematic reviews
- Evidence-based medicine

## Search Strategies

### Challenge Strategy
Legal searches focus on:
- Cases where similar experts were excluded
- Daubert failures
- Methodological criticisms
- Reliability challenges

Scientific searches focus on:
- False positive rates
- Methodological limitations
- Controversies in the field
- Alternative explanations

### Support Strategy
Legal searches focus on:
- Cases admitting similar experts
- Daubert successes
- Recognized methodologies
- Qualified expert precedents

Scientific searches focus on:
- Validation studies
- Peer acceptance
- Gold standard methods
- Clinical guidelines

## Usage Examples

### Standalone Testing
```python
from lexicon_external_research import test_external_research
import asyncio

# Test the module
asyncio.run(test_external_research())
```

### Integration with Pipeline
```python
from lexicon_pipeline import LEXICONPipeline

pipeline = LEXICONPipeline()

# The pipeline automatically uses external research
result = await pipeline.process_case(
    target_expert="Dr. Kenneth J.D. Allen",
    case_strategy="support",
    motion_type="Response to Daubert Motion"
)

# External research results are in:
legal_research = result['research']['legal_research']['raw_results']
scientific_research = result['research']['scientific_research']['raw_results']
```

### Direct Research
```python
from lexicon_external_research import conduct_external_research

results = await conduct_external_research(
    expert_name="Dr. Allen",
    methodologies=["DTI imaging", "Neuropsychological testing"],
    findings=["Diffuse axonal injury", "Cognitive deficits"],
    case_strategy="challenge"
)

# Access specific databases
courtlistener_cases = results['forensic_legal']['courtlistener']
pubmed_papers = results['scientific_domain']['pubmed']
```

## Output Format

### Legal Research Output
```json
{
  "courtlistener": [
    {
      "case_name": "Kumho Tire Co. v. Carmichael",
      "citation": "526 U.S. 137 (1999)",
      "court": "Supreme Court",
      "date": "1999-03-23",
      "excerpt": "Expert testimony must be reliable...",
      "relevance": 0.95
    }
  ],
  "google_scholar": [...],
  "summary": {
    "total_cases_found": 15,
    "databases_searched": ["CourtListener", "Google Scholar"],
    "key_precedents": ["Case1", "Case2"]
  }
}
```

### Scientific Research Output
```json
{
  "pubmed": [
    {
      "title": "False positive rates in TBI diagnosis",
      "authors": ["Smith JK", "Jones ML"],
      "journal": "Journal of Neuropsychology",
      "year": "2023",
      "pmid": "36789012",
      "relevance_to_case": "High - discusses limitations"
    }
  ],
  "arxiv": [...],
  "summary": {
    "total_papers_found": 23,
    "methodologies_researched": ["DTI imaging", "Testing"],
    "key_findings": ["Finding1", "Finding2"]
  }
}
```

## Rate Limits & Best Practices

1. **API Rate Limits**:
   - PubMed: 3 requests/second
   - CourtListener: 5,000/day
   - SERP API: Based on plan
   - ArXiv: Be respectful (no official limit)

2. **Caching**: Consider caching results to avoid repeated searches

3. **Error Handling**: Module includes fallbacks for API failures

4. **Ethical Use**: 
   - Respect robots.txt
   - Don't overwhelm servers
   - Use APIs when available

## Troubleshooting

### No Results Returned
- Check API keys in .env
- Verify internet connection
- Check API quotas

### Simulated Results
- Some databases require paid access
- Simulated results show what would be searched
- Consider getting API keys for full functionality

### Rate Limiting
- Add delays between requests
- Use batch processing
- Consider caching layer

## Future Enhancements

1. **Additional Databases**:
   - HeinOnline (legal)
   - Web of Science (scientific)
   - IEEE Xplore (technical)
   - ClinicalTrials.gov

2. **Advanced Features**:
   - Result deduplication
   - Citation graph analysis
   - Automated summarization
   - Real-time monitoring

3. **Integration**:
   - Direct Westlaw/Lexis integration
   - Institutional access
   - Federation search
   - Result ranking ML

---

The External Research Module ensures LEXICON's briefs are backed by comprehensive, current research from authoritative sources.