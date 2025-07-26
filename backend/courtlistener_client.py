"""
CourtListener API Client for LEXICON
Comprehensive access to all CourtListener API endpoints
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from urllib.parse import urljoin, quote
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class CourtListenerClient:
    """
    Client for accessing all CourtListener API endpoints
    Supports all /api/rest/v4/ resources
    """
    
    # Base API URL
    BASE_URL = "https://www.courtlistener.com/api/rest/v4/"
    
    # Available API endpoints
    ENDPOINTS = {
        # Core case data
        'dockets': 'dockets/',
        'docket_entries': 'docket-entries/',
        'recap_documents': 'recap-documents/',
        'opinions': 'opinions/',
        'opinion_clusters': 'clusters/',
        'citations': 'citations/',
        
        # Courts and judges
        'courts': 'courts/',
        'people': 'people/',  # Judges and attorneys
        'positions': 'positions/',  # Judge positions
        'schools': 'schools/',  # Law schools
        'political_affiliations': 'political-affiliations/',
        
        # Parties and attorneys
        'parties': 'parties/',
        'attorneys': 'attorneys/',
        'attorney_organizations': 'attorney-organizations/',
        
        # Audio and RECAP
        'audio': 'audio/',
        'recap': 'recap/',
        'recap_fetch': 'recap-fetch/',
        
        # Search endpoints
        'search': 'search/',
        'search_opinions': 'search/opinions/',
        'search_recap': 'search/recap/',
        'search_dockets': 'search/dockets/',
        'search_audio': 'search/audio/',
        'search_people': 'search/people/',
        
        # Alerts and tags
        'docket_alerts': 'docket-alerts/',
        'tags': 'tags/',
        
        # Visualizations
        'visualizations': 'visualizations/scotus-mapper/',
        
        # Financial disclosures
        'financial_disclosures': 'financial-disclosures/',
        'investments': 'investments/',
        'debts': 'debts/',
        'gifts': 'gifts/',
        'reimbursements': 'reimbursements/',
        
        # Other
        'fjc_integrated_database': 'fjc-integrated-database/',
        'originating_court_information': 'originating-court-information/',
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CourtListener client
        
        Args:
            api_key: CourtListener API key (optional for read-only access)
        """
        self.api_key = api_key or os.getenv("COURTLISTENER_API_KEY")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Token {self.api_key}'
            })
        
        self.session.headers.update({
            'User-Agent': 'LEXICON Legal AI/1.0 (https://lexicon-ai.com)',
            'Accept': 'application/json'
        })
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None, full_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Make API request with retry logic
        """
        if full_url:
            url = full_url
        else:
            url = urljoin(self.BASE_URL, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"CourtListener API error: {str(e)}")
            raise
    
    def get(self, endpoint: str, **params) -> Dict[str, Any]:
        """
        Generic GET request to any endpoint
        
        Args:
            endpoint: API endpoint (e.g., 'dockets/', 'opinions/')
            **params: Query parameters
        
        Returns:
            API response data
        """
        return self._make_request('GET', endpoint, params=params)
    
    def get_by_url(self, url: str) -> Dict[str, Any]:
        """
        GET request to a full URL (useful for pagination)
        
        Args:
            url: Full URL to request
        
        Returns:
            API response data
        """
        return self._make_request('GET', '', full_url=url)
    
    def search_all(self, query: str, filters: Optional[Dict] = None) -> Dict[str, List[Dict]]:
        """
        Search across all available endpoints for tort-relevant data
        
        Args:
            query: Search query (e.g., "traumatic brain injury expert")
            filters: Additional filters by endpoint
        
        Returns:
            Combined results from all endpoints
        """
        results = {}
        filters = filters or {}
        
        # Search opinions
        try:
            opinions = self.search_opinions(query, **filters.get('opinions', {}))
            results['opinions'] = opinions.get('results', [])
        except Exception as e:
            logger.warning(f"Opinion search failed: {e}")
            results['opinions'] = []
        
        # Search dockets
        try:
            dockets = self.search_dockets(query, **filters.get('dockets', {}))
            results['dockets'] = dockets.get('results', [])
        except Exception as e:
            logger.warning(f"Docket search failed: {e}")
            results['dockets'] = []
        
        # Search RECAP documents
        try:
            recap = self.search_recap(query, **filters.get('recap', {}))
            results['recap_documents'] = recap.get('results', [])
        except Exception as e:
            logger.warning(f"RECAP search failed: {e}")
            results['recap_documents'] = []
        
        # Search people (judges)
        try:
            people = self.search_people(query, **filters.get('people', {}))
            results['judges'] = people.get('results', [])
        except Exception as e:
            logger.warning(f"People search failed: {e}")
            results['judges'] = []
        
        return results
    
    def search_opinions(self, query: str, **filters) -> Dict[str, Any]:
        """Search published opinions"""
        params = {'q': query}
        params.update(filters)
        return self.get('search/', type='o', **params)
    
    def search_dockets(self, query: str, **filters) -> Dict[str, Any]:
        """Search docket information"""
        params = {'q': query}
        params.update(filters)
        return self.get('search/', type='d', **params)
    
    def search_recap(self, query: str, **filters) -> Dict[str, Any]:
        """Search RECAP documents"""
        params = {'q': query}
        params.update(filters)
        return self.get('search/', type='r', **params)
    
    def search_people(self, query: str, **filters) -> Dict[str, Any]:
        """Search judges and attorneys"""
        params = {'q': query}
        params.update(filters)
        return self.get('search/', type='p', **params)
    
    def get_docket(self, docket_id: int) -> Dict[str, Any]:
        """Get detailed docket information"""
        return self.get(f'dockets/{docket_id}/')
    
    def get_opinion(self, opinion_id: int) -> Dict[str, Any]:
        """Get detailed opinion information"""
        return self.get(f'opinions/{opinion_id}/')
    
    def get_person(self, person_id: int) -> Dict[str, Any]:
        """Get detailed information about a judge or attorney"""
        return self.get(f'people/{person_id}/')
    
    def get_court(self, court_id: str) -> Dict[str, Any]:
        """Get court information"""
        return self.get(f'courts/{court_id}/')
    
    def search_tort_cases(self, injury_type: str = "traumatic brain injury", 
                         jurisdiction: Optional[str] = None,
                         date_filed_after: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Specialized search for tort cases
        
        Args:
            injury_type: Type of injury to search for
            jurisdiction: Court jurisdiction
            date_filed_after: Filter cases filed after this date (YYYY-MM-DD)
        
        Returns:
            Relevant tort cases from multiple sources
        """
        # Build sophisticated query
        query_parts = [injury_type]
        
        # Add tort-specific terms
        tort_terms = [
            "negligence", "damages", "liability", "personal injury",
            "expert witness", "daubert", "frye", "causation"
        ]
        
        # Create comprehensive query
        full_query = f'"{injury_type}" AND ({" OR ".join(tort_terms)})'
        
        filters = {
            'opinions': {
                'filed_after': date_filed_after,
                'type': 'opinion'  # Published opinions only
            },
            'dockets': {
                'date_filed__gte': date_filed_after,
                'nature_of_suit': '440'  # Personal injury
            },
            'recap': {
                'description__icontains': 'expert',
                'document_type': ['motion', 'memorandum', 'order']
            }
        }
        
        if jurisdiction:
            filters['opinions']['court'] = jurisdiction
            filters['dockets']['court'] = jurisdiction
        
        return self.search_all(full_query, filters)
    
    def find_expert_challenges(self, expert_name: str) -> Dict[str, List[Dict]]:
        """
        Find cases where a specific expert was challenged
        
        Args:
            expert_name: Name of the expert witness
        
        Returns:
            Cases mentioning the expert
        """
        # Search for Daubert/Frye motions mentioning the expert
        daubert_query = f'"{expert_name}" AND (daubert OR frye OR "motion to exclude")'
        
        return self.search_all(daubert_query, {
            'recap': {
                'document_type': ['motion', 'order'],
                'description__icontains': 'expert'
            }
        })
    
    def get_judge_history(self, judge_name: str, on_expert_motions: bool = True) -> Dict[str, Any]:
        """
        Get a judge's history on expert witness rulings
        
        Args:
            judge_name: Name of the judge
            on_expert_motions: Filter for expert-related cases only
        
        Returns:
            Judge's cases and rulings
        """
        # First, find the judge
        people_results = self.search_people(judge_name)
        
        if not people_results.get('results'):
            return {'error': 'Judge not found'}
        
        judge_id = people_results['results'][0]['id']
        judge_data = self.get_person(judge_id)
        
        # Find cases by this judge
        if on_expert_motions:
            query = 'daubert OR frye OR "expert witness"'
        else:
            query = '*'
        
        opinions = self.search_opinions(
            query,
            author_id=judge_id,
            per_curiam=False
        )
        
        return {
            'judge': judge_data,
            'opinions': opinions.get('results', []),
            'total_cases': opinions.get('count', 0)
        }
    
    def download_document(self, document_url: str, save_path: str) -> bool:
        """
        Download a document from CourtListener
        
        Args:
            document_url: URL of the document
            save_path: Where to save the document
        
        Returns:
            Success status
        """
        try:
            response = self.session.get(document_url, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            logger.error(f"Failed to download document: {e}")
            return False
    
    def paginate_results(self, initial_response: Dict[str, Any], 
                        max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        Paginate through all results
        
        Args:
            initial_response: First page of results
            max_pages: Maximum pages to retrieve
        
        Returns:
            All results combined
        """
        all_results = initial_response.get('results', [])
        next_url = initial_response.get('next')
        page = 1
        
        while next_url and page < max_pages:
            try:
                response = self.get_by_url(next_url)
                all_results.extend(response.get('results', []))
                next_url = response.get('next')
                page += 1
            except Exception as e:
                logger.warning(f"Pagination failed at page {page}: {e}")
                break
        
        return all_results


# Example usage for LEXICON
def search_tbi_precedents(client: CourtListenerClient) -> Dict[str, Any]:
    """
    Search for TBI-related legal precedents
    """
    # Search for traumatic brain injury expert challenges
    tbi_cases = client.search_tort_cases(
        injury_type="traumatic brain injury",
        date_filed_after="2015-01-01"
    )
    
    # Find specific expert challenges
    expert_challenges = client.find_expert_challenges("neuropsychologist")
    
    # Combine and analyze results
    return {
        'tbi_opinions': tbi_cases.get('opinions', []),
        'tbi_dockets': tbi_cases.get('dockets', []),
        'expert_challenges': expert_challenges,
        'total_results': sum(len(v) for v in tbi_cases.values())
    }


if __name__ == "__main__":
    # Test the client
    client = CourtListenerClient()
    
    # Example: Search for all TBI-related tort cases
    results = search_tbi_precedents(client)
    
    print(f"Found {results['total_results']} relevant cases")
    print(f"Opinions: {len(results['tbi_opinions'])}")
    print(f"Dockets: {len(results['tbi_dockets'])}")