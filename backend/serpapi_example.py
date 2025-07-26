"""
Example of using SerpAPI for Google Scholar searches
Requires API key from https://serpapi.com/manage-api-key
"""

import requests
import json
from typing import Dict, List

class GoogleScholarSearch:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search.json"
    
    def search_daubert_cases(self, query: str = "daubert standard expert witness", num_results: int = 10) -> List[Dict]:
        """Search Google Scholar for Daubert-related cases and articles"""
        params = {
            'engine': 'google_scholar',
            'q': query,
            'api_key': self.api_key,
            'num': num_results,
            'scisbd': 1,  # Sort by date
            'as_ylo': 2020  # Results from 2020 onwards
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return self._parse_results(data)
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    
    def search_expert_methodology(self, expert_name: str, methodology: str) -> List[Dict]:
        """Search for validation of specific expert methodologies"""
        query = f'"{expert_name}" OR "{methodology}" AND ("daubert" OR "reliability" OR "validity")'
        return self.search_daubert_cases(query)
    
    def search_tbi_daubert(self) -> List[Dict]:
        """Search specifically for TBI-related Daubert cases"""
        query = '"traumatic brain injury" AND "daubert" AND ("expert witness" OR "expert testimony")'
        return self.search_daubert_cases(query)
    
    def _parse_results(self, data: Dict) -> List[Dict]:
        """Parse SerpAPI response into structured format"""
        results = []
        
        if 'organic_results' in data:
            for item in data['organic_results']:
                result = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'publication': item.get('publication_info', {}).get('summary', ''),
                    'authors': item.get('publication_info', {}).get('authors', []),
                    'cited_by': item.get('inline_links', {}).get('cited_by', {}).get('total', 0),
                    'pdf_link': item.get('resources', [{}])[0].get('link', '') if item.get('resources') else ''
                }
                results.append(result)
        
        return results

# Example usage:
if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = "your_serpapi_key_here"
    
    searcher = GoogleScholarSearch(API_KEY)
    
    try:
        # Search for general Daubert cases
        print("Searching for Daubert standard cases...")
        daubert_results = searcher.search_daubert_cases()
        
        print(f"\nFound {len(daubert_results)} results:")
        for i, result in enumerate(daubert_results[:3], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Authors: {', '.join(result['authors'][:3])}")
            print(f"   Citations: {result['cited_by']}")
            print(f"   Link: {result['link']}")
            if result['pdf_link']:
                print(f"   PDF: {result['pdf_link']}")
        
        # Search for TBI-specific Daubert cases
        print("\n\nSearching for TBI Daubert cases...")
        tbi_results = searcher.search_tbi_daubert()
        print(f"Found {len(tbi_results)} TBI-related results")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTo use this script:")
        print("1. Sign up at https://serpapi.com")
        print("2. Get your API key from https://serpapi.com/manage-api-key")
        print("3. Replace 'your_serpapi_key_here' with your actual API key")