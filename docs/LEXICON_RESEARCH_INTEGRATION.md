# LEXICON Research Integration Guide

## Overview
LEXICON uses a multi-agent architecture where each agent has specific research capabilities. All agents use the same SerpAPI key for Google Scholar access, but with different search strategies.

## API Configuration
- **SerpAPI Key**: `c6434b985f91dda9d0f7c0a8f5be1ecceac8d4a57ef27b5d11b8d9a207eab807`
- **No separate Google Scholar API needed** - SerpAPI provides access

## Agent Research Capabilities

### Agent 1: Claude Opus 4 (Orchestrator)
- Searches internal ChromaDB corpus (8,505 documents)
- Coordinates other agents
- No external API calls

### Agent 2: O3 Pro Deep Research (Forensic/Legal)
**Google Scholar Legal Focus:**
```python
# Example queries for CHALLENGE strategy:
'"Dr. Allen" Daubert motion exclude testimony'
'neuropsychologist expert witness excluded "TBI"'
'traumatic brain injury expert unreliable methodology court'

# Example queries for SUPPORT strategy:
'"Dr. Allen" expert testimony admitted reliable'
'neuropsychologist qualified Daubert motion denied'
'traumatic brain injury expert accepted methodology'
```

**Also searches:**
- CourtListener (simulated)
- Westlaw (simulated)
- PACER (simulated)

### Agent 3: GPT-4.1 (Scientific Domain)
**Google Scholar Scientific Focus:**
```python
# Example queries for CHALLENGE strategy:
'"DTI imaging" false positive rate traumatic brain injury'
'"WAIS-IV" limitations mild TBI diagnosis'
'"neuropsychological testing" reliability controversy'

# Example queries for SUPPORT strategy:
'"DTI imaging" validated traumatic brain injury diagnosis'
'"WAIS-IV" sensitivity specificity TBI'
'"neuropsychological testing" gold standard assessment'
```

**Enhanced features:**
- Quality scoring (citations, journal impact, recency)
- Relevance scoring (query matching, methodology mentions)
- Deduplication and ranking
- PDF availability checking

**Also searches:**
- PubMed (API or simulated)
- ArXiv (free API)
- Cochrane Reviews (simulated)

### Agent 4: GPT-4.5 Research Preview (Initial Draft)
- Uses research from Agents 2 & 3
- No direct external searches

### Agent 5: Gemini 2.5 Pro (Final Review)
- Fact-checks against all sources
- No direct external searches

## Recent Findings (July 2025)

### Key TBI Daubert Papers Found:
1. **Ross et al. (2022)** - NeuroQuant/NeuroGage validation (7 citations)
2. **van Velkinburgh & Herbst (2023)** - DTI courtroom admissibility (2 citations)
3. **McBride et al. (2023)** - Blood biomarkers legal implications (8 citations)
4. **Chafetz et al. (2025)** - AACN neuropsych best practices
5. **Kurtz & Pintarelli (2024)** - PAI assessment Daubert standards (6 citations)

### Scientific Validation Papers:
1. **Vinet et al. (2024)** - DTI validation for TBI diagnosis
2. **Wang et al. (2024)** - White/gray matter MRI-DTI indicators (13 citations)
3. **Bergauer et al. (2022)** - Fluid/imaging biomarkers in CTE (16 citations)

## Implementation in Pipeline

```python
# In lexicon_pipeline.py, Stage 2 & 3:

# Agent 2 - Legal Research
legal_results = await external_research.forensic_legal_research(
    expert_name="Dr. Kenneth J.D. Allen",
    methodologies=["DTI imaging", "Neuropsychological testing"],
    case_strategy="support"  # or "challenge"
)

# Agent 3 - Scientific Research  
scientific_results = await external_research.scientific_domain_research(
    expert_name="Dr. Kenneth J.D. Allen",
    methodologies=["DTI imaging", "WAIS-IV", "Trail Making Test"],
    findings=["Diffuse axonal injury", "Cognitive deficits"],
    case_strategy="support"  # or "challenge"
)
```

## Search Parameters

### SerpAPI Google Scholar Parameters:
- `engine`: 'google_scholar'
- `q`: Search query
- `api_key`: Your SerpAPI key
- `num`: Number of results (typically 5-10)
- `as_ylo`: Year lower bound (e.g., 2020)
- `scisbd`: 1 (sort by date)
- `as_vis`: 1 (exclude citations)
- `as_occt`: 'title' (search in title for reviews)

### Quality Indicators:
- **High Impact Journals**: Nature, Science, NEJM, JAMA, Brain, Neurology
- **Citation Thresholds**: >100 (high), >50 (medium), >10 (low)
- **Publication Types**: Reviews and meta-analyses get priority
- **Recency Bonus**: Papers from 2023-2025

## Best Practices

1. **Rate Limiting**: 
   - Limit queries to avoid hitting API limits
   - Cache results when possible

2. **Query Construction**:
   - Use quotes for exact phrases
   - Combine methodologies with outcome terms
   - Include "traumatic brain injury" or "TBI" for relevance

3. **Strategy Alignment**:
   - CHALLENGE: Focus on limitations, false positives, controversies
   - SUPPORT: Focus on validation, reliability, acceptance

4. **Result Processing**:
   - Check PDF availability for key papers
   - Prioritize highly cited recent papers
   - Cross-reference findings between agents

## Testing Commands

```bash
# Test external research module
python lexicon_external_research.py

# Test Agent 3 scientific search
python test_agent3_scientific_search.py

# Test TBI Daubert searches
python test_tbi_daubert_search.py

# Run full pipeline with external research
python test_lexicon_pipeline.py
```

## Web Interface Integration
The web app at http://localhost:5000 uses these external research capabilities when generating briefs. Real-time progress updates show when each agent is conducting their research phase.