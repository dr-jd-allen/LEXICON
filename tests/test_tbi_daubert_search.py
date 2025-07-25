"""
Test TBI Daubert searches using SerpAPI
"""

import requests
import json
from datetime import datetime

API_KEY = 'c6434b985f91dda9d0f7c0a8f5be1ecceac8d4a57ef27b5d11b8d9a207eab807'

def search_tbi_daubert_cases():
    """Search for recent TBI Daubert cases"""
    
    # Define search queries
    queries = [
        '"traumatic brain injury" AND "daubert motion" AND "expert testimony"',
        '"TBI" AND "expert witness" AND "excluded" AND "neuropsychological"',
        '"mild traumatic brain injury" AND "daubert standard" AND "reliability"',
        '"DTI imaging" AND "daubert" AND "traumatic brain injury"',
        '"neuropsychologist" AND "daubert challenge" AND "TBI" case law'
    ]
    
    all_results = []
    
    for query in queries:
        print(f"\nSearching: {query[:60]}...")
        
        params = {
            'engine': 'google_scholar',
            'q': query,
            'api_key': API_KEY,
            'num': 5,
            'as_ylo': 2020,  # Results from 2020 onwards
            'scisbd': 1      # Sort by date
        }
        
        response = requests.get('https://serpapi.com/search.json', params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'organic_results' in data:
                print(f"Found {len(data['organic_results'])} results")
                
                for result in data['organic_results'][:3]:
                    result_info = {
                        'query': query,
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'link': result.get('link', ''),
                        'publication': result.get('publication_info', {}).get('summary', ''),
                        'cited_by': result.get('inline_links', {}).get('cited_by', {}).get('total', 0),
                        'pdf_available': bool(result.get('resources', [])),
                        'pdf_link': result.get('resources', [{}])[0].get('link', '') if result.get('resources') else ''
                    }
                    all_results.append(result_info)
        else:
            print(f"Error: {response.status_code}")
    
    return all_results

def analyze_results(results):
    """Analyze and categorize the search results"""
    
    print("\n" + "="*80)
    print("TBI DAUBERT CASE ANALYSIS")
    print("="*80)
    
    # Categorize results
    exclusion_cases = []
    admission_cases = []
    methodology_papers = []
    
    for result in results:
        title_lower = result['title'].lower()
        snippet_lower = result['snippet'].lower()
        
        # Categorize based on content
        if 'exclud' in title_lower or 'exclud' in snippet_lower:
            exclusion_cases.append(result)
        elif 'admit' in title_lower or 'reliab' in title_lower:
            admission_cases.append(result)
        elif 'methodolog' in title_lower or 'standard' in title_lower:
            methodology_papers.append(result)
    
    # Print categorized results
    print(f"\n1. EXPERT EXCLUSION CASES ({len(exclusion_cases)} found):")
    print("-" * 50)
    for i, case in enumerate(exclusion_cases[:5], 1):
        print(f"\n{i}. {case['title']}")
        print(f"   Source: {case['publication']}")
        print(f"   Citations: {case['cited_by']}")
        if case['pdf_available']:
            print(f"   PDF: Available")
        print(f"   Relevance: {case['snippet'][:150]}...")
    
    print(f"\n2. EXPERT ADMISSION CASES ({len(admission_cases)} found):")
    print("-" * 50)
    for i, case in enumerate(admission_cases[:5], 1):
        print(f"\n{i}. {case['title']}")
        print(f"   Source: {case['publication']}")
        print(f"   Citations: {case['cited_by']}")
    
    print(f"\n3. METHODOLOGY & STANDARDS ({len(methodology_papers)} found):")
    print("-" * 50)
    for i, paper in enumerate(methodology_papers[:5], 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Source: {paper['publication']}")
    
    # Find most cited papers
    print("\n4. MOST INFLUENTIAL (By Citations):")
    print("-" * 50)
    sorted_by_citations = sorted(results, key=lambda x: x['cited_by'], reverse=True)
    for i, paper in enumerate(sorted_by_citations[:5], 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Citations: {paper['cited_by']}")
        print(f"   Link: {paper['link']}")

def save_results(results):
    """Save results to JSON file"""
    filename = f"tbi_daubert_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'search_date': datetime.now().isoformat(),
            'total_results': len(results),
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nResults saved to: {filename}")

if __name__ == "__main__":
    print("Searching for TBI Daubert cases and expert testimony...")
    print("Using Google Scholar via SerpAPI")
    print("-" * 60)
    
    # Search for cases
    results = search_tbi_daubert_cases()
    
    # Analyze results
    analyze_results(results)
    
    # Save results
    save_results(results)
    
    print("\n\nSearch complete!")