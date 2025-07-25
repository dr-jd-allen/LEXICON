"""
Test Agent 3 (GPT-4.1) Scientific Domain Research
Enhanced Google Scholar capabilities for academic/scientific papers
"""

import asyncio
from lexicon_external_research import ExternalResearchModule
import json
from datetime import datetime

async def test_scientific_search():
    """Test Agent 3's scientific research capabilities"""
    
    print("=" * 80)
    print("AGENT 3 (GPT-4.1) - SCIENTIFIC DOMAIN RESEARCH TEST")
    print("=" * 80)
    print("Using Google Scholar via SerpAPI for academic/scientific papers")
    print()
    
    # Test scenarios
    test_cases = [
        {
            'name': 'DTI Imaging Validation',
            'expert': 'Dr. Kenneth J.D. Allen',
            'methodologies': ['DTI imaging', 'Fractional anisotropy', 'White matter integrity'],
            'findings': ['Diffuse axonal injury', 'White matter lesions'],
            'strategy': 'support'
        },
        {
            'name': 'Neuropsychological Testing Limitations',
            'expert': 'Dr. Sarah Johnson',
            'methodologies': ['WAIS-IV', 'Trail Making Test', 'Rey Complex Figure'],
            'findings': ['Cognitive deficits', 'Executive dysfunction'],
            'strategy': 'challenge'
        }
    ]
    
    async with ExternalResearchModule() as research:
        for test in test_cases:
            print(f"\n{'='*60}")
            print(f"TEST: {test['name']}")
            print(f"Strategy: {test['strategy'].upper()}")
            print(f"Methodologies: {', '.join(test['methodologies'])}")
            print("="*60)
            
            # Run scientific research
            results = await research.scientific_domain_research(
                expert_name=test['expert'],
                methodologies=test['methodologies'],
                findings=test['findings'],
                case_strategy=test['strategy']
            )
            
            # Display Google Scholar results
            print(f"\nGOOGLE SCHOLAR SCIENTIFIC RESULTS:")
            print("-" * 40)
            
            scholar_results = results.get('google_scholar_scientific', [])
            
            if scholar_results:
                # Group by quality score
                high_quality = [r for r in scholar_results if r.get('quality_score', 0) >= 0.7]
                medium_quality = [r for r in scholar_results if 0.3 <= r.get('quality_score', 0) < 0.7]
                
                if high_quality:
                    print(f"\nHIGH QUALITY PAPERS ({len(high_quality)}):")
                    for i, paper in enumerate(high_quality[:5], 1):
                        print(f"\n{i}. {paper['title']}")
                        print(f"   Authors: {', '.join(paper.get('authors', [])[:3])}")
                        print(f"   Journal: {paper.get('journal', 'N/A')} ({paper.get('year', 'N/A')})")
                        print(f"   Citations: {paper.get('cited_by', 0)}")
                        print(f"   Quality Score: {paper.get('quality_score', 0):.2f}")
                        print(f"   Relevance Score: {paper.get('relevance_score', 0):.2f}")
                        if paper.get('pdf_link'):
                            print(f"   PDF: Available")
                        print(f"   Type: {paper.get('type', 'article')}")
                        
                        # Show methodology mentions
                        if paper.get('methodology_mentioned'):
                            print(f"   [METHODOLOGY MATCH]")
                
                if medium_quality:
                    print(f"\n\nMEDIUM QUALITY PAPERS ({len(medium_quality)}):")
                    for paper in medium_quality[:3]:
                        print(f"   - {paper['title']} (Citations: {paper.get('cited_by', 0)})")
            
            # Show other sources
            print(f"\n\nOTHER SCIENTIFIC SOURCES:")
            print(f"PubMed results: {len(results.get('pubmed', []))}")
            print(f"ArXiv results: {len(results.get('arxiv', []))}")
            print(f"Cochrane reviews: {len(results.get('cochrane', []))}")
            
            # Summary statistics
            summary = results.get('summary', {})
            print(f"\n\nSUMMARY:")
            print(f"Total papers found: {summary.get('total_papers_found', 0)}")
            print(f"Search focus: {summary.get('search_focus', 'N/A')}")
            print(f"Key findings: {len(summary.get('key_findings', []))}")

async def demonstrate_query_building():
    """Show how Agent 3 builds scientific queries"""
    
    print("\n\n" + "="*80)
    print("SCIENTIFIC QUERY BUILDING DEMONSTRATION")
    print("="*80)
    
    methodologies = ["DTI imaging", "Neuropsychological testing", "fMRI"]
    
    print("\nFor CHALLENGE strategy, Agent 3 builds queries like:")
    print("-" * 40)
    challenge_queries = [
        f'"{methodologies[0]}" false positive rate traumatic brain injury',
        f'"{methodologies[0]}" limitations mild TBI diagnosis',
        f'"{methodologies[1]}" reliability controversy neuropsychology',
        f'limitations of {methodologies[2]} in forensic settings'
    ]
    for q in challenge_queries:
        print(f"  • {q}")
    
    print("\n\nFor SUPPORT strategy, Agent 3 builds queries like:")
    print("-" * 40)
    support_queries = [
        f'"{methodologies[0]}" validated traumatic brain injury diagnosis',
        f'"{methodologies[0]}" sensitivity specificity TBI',
        f'"{methodologies[1]}" gold standard neuropsychological assessment',
        f'reliability of {methodologies[2]} in clinical practice'
    ]
    for q in support_queries:
        print(f"  • {q}")
    
    print("\n\nKEY FEATURES:")
    print("-" * 40)
    print("1. Quality scoring based on:")
    print("   - Citation count (>100 = high impact)")
    print("   - Journal prestige (Nature, Science, JAMA, etc.)")
    print("   - Publication type (reviews get bonus)")
    print("   - Recency (2023-2025 papers prioritized)")
    print("   - Methodology keywords (systematic, meta-analysis, etc.)")
    
    print("\n2. Relevance scoring based on:")
    print("   - Query term matching")
    print("   - Methodology mentions")
    print("   - TBI-specific terminology")
    print("   - Title vs. abstract matching")
    
    print("\n3. Deduplication and sorting:")
    print("   - Removes duplicate papers")
    print("   - Sorts by quality AND relevance")
    print("   - Returns top 20 unique results")

def save_results(results, filename):
    """Save results to JSON for analysis"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'agent': 'Agent 3 (GPT-4.1) Scientific Domain',
            'results': results
        }, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {filename}")

if __name__ == "__main__":
    print("Testing Agent 3 Scientific Domain Research...")
    print("This demonstrates enhanced Google Scholar integration")
    print("-" * 60)
    
    # Run main test
    asyncio.run(test_scientific_search())
    
    # Show query building
    asyncio.run(demonstrate_query_building())
    
    print("\n\nCONCLUSION:")
    print("="*60)
    print("Agent 3 now has comprehensive scientific search capabilities:")
    print("✓ Enhanced Google Scholar integration via SerpAPI")
    print("✓ Quality and relevance scoring")
    print("✓ Support for both challenge and support strategies")
    print("✓ Automatic deduplication and ranking")
    print("✓ Rich metadata extraction (authors, journals, citations)")
    print("✓ PDF availability checking")
    print("\nNo separate Google Scholar API key needed - just SerpAPI!")