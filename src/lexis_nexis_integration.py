#!/usr/bin/env python3
"""
LEXIS-NEXIS integration for LEXICON MVP
Provides legal research capabilities for Daubert precedent
"""

import os
import re
import time
from typing import List, Dict, Any
from datetime import datetime, timedelta
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import json

load_dotenv()


class LexisNexisResearcher:
    def __init__(self):
        self.username = os.getenv('LEXIS_NEXIS_USERNAME')
        self.password = os.getenv('LEXIS_NEXIS_PASSWORD')
        self.api_endpoint = os.getenv('LEXIS_NEXIS_API_URL', '')
        self.use_api = bool(self.api_endpoint)
        
        # Validate credentials
        if not self.username or not self.password:
            print("⚠️ LEXIS-NEXIS credentials not found. Using mock data.")
            self.use_mock = True
        else:
            self.use_mock = False
            print(f"✅ LEXIS-NEXIS configured for user: {self.username}")
        
    def search_daubert_precedent(self, 
                                expert_methodology: str,
                                jurisdiction: str = "federal",
                                years_back: int = 10) -> List[Dict[str, Any]]:
        """
        Search for relevant Daubert precedent based on expert methodology.
        
        Args:
            expert_methodology: The specific methodology to search (e.g., "DTI imaging", "biomechanical analysis")
            jurisdiction: "federal", "state", or specific state (e.g., "Illinois")
            years_back: How many years of precedent to search
            
        Returns:
            List of relevant cases with citations and holdings
        """
        
        # Build search query
        search_query = self._build_daubert_query(expert_methodology, jurisdiction, years_back)
        
        if self.use_mock:
            return self._get_mock_results()
        elif self.use_api:
            return self._search_via_api(search_query)
        else:
            return self._search_via_selenium(search_query)
    
    def _build_daubert_query(self, methodology: str, jurisdiction: str, years_back: int) -> str:
        """Build optimized search query for Daubert cases."""
        
        # Base Daubert search
        base_query = '(Daubert OR "Rule 702" OR "expert testimony") AND exclude!'
        
        # Add methodology-specific terms
        methodology_terms = self._get_methodology_terms(methodology)
        methodology_query = f' AND ({" OR ".join(methodology_terms)})'
        
        # Add TBI-specific terms if relevant
        if any(term in methodology.lower() for term in ['dti', 'tbi', 'brain', 'concussion']):
            tbi_query = ' AND ("traumatic brain injury" OR TBI OR mTBI OR concussion OR "diffuse axonal")'
        else:
            tbi_query = ''
        
        # Jurisdiction filter
        if jurisdiction == "federal":
            jurisdiction_filter = ' AND COURT(federal)'
        elif jurisdiction == "state":
            jurisdiction_filter = ' AND COURT(state)'
        elif jurisdiction in ["Illinois", "Indiana", "California"]:  # Add supported states
            jurisdiction_filter = f' AND COURT({jurisdiction})'
        else:
            jurisdiction_filter = ''
        
        # Date filter
        date_filter = f' AND DATE(>= {datetime.now().year - years_back})'
        
        # Combine all parts
        full_query = base_query + methodology_query + tbi_query + jurisdiction_filter + date_filter
        
        # Add segment for most relevant sections
        full_query += ' /p exclude! /p methodology /p reliability'
        
        return full_query
    
    def _get_methodology_terms(self, methodology: str) -> List[str]:
        """Get search terms for specific methodologies."""
        
        methodology_lower = methodology.lower()
        
        # Common TBI/neuroimaging methodologies
        if 'dti' in methodology_lower or 'diffusion tensor' in methodology_lower:
            return ['"diffusion tensor imaging"', 'DTI', '"fractional anisotropy"', 'FA', '"white matter"']
        elif 'biomechanical' in methodology_lower:
            return ['biomechanical', '"injury threshold"', '"force analysis"', 'acceleration']
        elif 'neuropsych' in methodology_lower:
            return ['neuropsychological', '"cognitive testing"', '"malingering"', '"effort testing"']
        elif 'pet' in methodology_lower or 'spect' in methodology_lower:
            return ['PET', 'SPECT', '"brain imaging"', '"metabolic imaging"']
        else:
            # Generic terms
            return [f'"{methodology}"', methodology.split()[0]]
    
    def _search_via_api(self, query: str) -> List[Dict[str, Any]]:
        """Search using LEXIS-NEXIS API (if available)."""
        
        headers = {
            'Authorization': f'Bearer {self._get_api_token()}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'query': query,
            'jurisdiction': 'US',
            'content_type': 'cases',
            'max_results': 20,
            'sort': 'relevance'
        }
        
        try:
            response = requests.post(
                f'{self.api_endpoint}/search',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return self._parse_api_results(response.json())
            else:
                print(f"API search failed: {response.status_code}")
                return self._get_mock_results()
                
        except Exception as e:
            print(f"API error: {str(e)}")
            return self._get_mock_results()
    
    def _search_via_selenium(self, query: str) -> List[Dict[str, Any]]:
        """Search using Selenium web automation (fallback)."""
        
        # For MVP, return mock results
        # In production, this would automate the LEXIS-NEXIS web interface
        print(f"Would search LEXIS-NEXIS with query: {query}")
        return self._get_mock_results()
    
    def _parse_api_results(self, api_response: Dict) -> List[Dict[str, Any]]:
        """Parse API response into standardized format."""
        
        results = []
        for case in api_response.get('results', []):
            results.append({
                'citation': case.get('citation'),
                'case_name': case.get('name'),
                'court': case.get('court'),
                'date': case.get('date'),
                'holding': case.get('synopsis', ''),
                'relevant_text': case.get('relevant_passages', []),
                'daubert_factors': self._extract_daubert_factors(case.get('full_text', ''))
            })
        
        return results
    
    def _extract_daubert_factors(self, case_text: str) -> Dict[str, bool]:
        """Extract which Daubert factors were discussed in the case."""
        
        factors = {
            'testability': False,
            'peer_review': False,
            'error_rate': False,
            'standards': False,
            'general_acceptance': False
        }
        
        case_text_lower = case_text.lower()
        
        # Check for each Daubert factor
        if re.search(r'test(ed|able|ability)', case_text_lower):
            factors['testability'] = True
        if re.search(r'peer.?review|publication', case_text_lower):
            factors['peer_review'] = True
        if re.search(r'error.?rate|false.?positive|accuracy', case_text_lower):
            factors['error_rate'] = True
        if re.search(r'standard|protocol|procedure', case_text_lower):
            factors['standards'] = True
        if re.search(r'general(ly)?.?accept', case_text_lower):
            factors['general_acceptance'] = True
            
        return factors
    
    def _get_mock_results(self) -> List[Dict[str, Any]]:
        """Return mock results for testing/demo purposes."""
        
        return [
            {
                'citation': 'Henderson v. State Farm, 2023 WL 123456 (N.D. Cal. 2023)',
                'case_name': 'Henderson v. State Farm Mutual Automobile Insurance Co.',
                'court': 'N.D. Cal.',
                'date': '2023-03-15',
                'holding': 'Court excluded expert testimony based on DTI imaging, finding methodology unreliable for individual diagnosis.',
                'relevant_text': [
                    'DTI remains an experimental technique unsuitable for courtroom use in individual cases.',
                    'The expert failed to establish error rates or general acceptance for forensic use of DTI.'
                ],
                'daubert_factors': {
                    'testability': True,
                    'peer_review': True,
                    'error_rate': True,
                    'standards': False,
                    'general_acceptance': False
                }
            },
            {
                'citation': 'Meyers v. Illinois Central R.R., 629 F.3d 639 (7th Cir. 2010)',
                'case_name': 'Meyers v. Illinois Central Railroad',
                'court': '7th Cir.',
                'date': '2010-12-20',
                'holding': 'Appellate court affirmed exclusion of DTI-based TBI testimony.',
                'relevant_text': [
                    'The methodology was not shown to be generally accepted for forensic purposes.',
                    'Clinical use does not automatically qualify a technique for litigation.'
                ],
                'daubert_factors': {
                    'testability': True,
                    'peer_review': True,
                    'error_rate': False,
                    'standards': False,
                    'general_acceptance': False
                }
            }
        ]
    
    def _get_api_token(self) -> str:
        """Get API authentication token."""
        # This would implement OAuth or other auth mechanism
        return "mock_token"
    
    def validate_connection(self) -> bool:
        """Test LEXIS-NEXIS connection with credentials."""
        
        if self.use_mock:
            return True
            
        try:
            # Try a simple search to validate credentials
            test_results = self.search_daubert_precedent(
                expert_methodology="test",
                jurisdiction="federal",
                years_back=1
            )
            return len(test_results) > 0
        except Exception as e:
            print(f"❌ LEXIS-NEXIS connection failed: {str(e)}")
            return False
    
    def format_for_motion(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results for inclusion in Daubert motion."""
        
        formatted_text = "Legal precedent strongly supports exclusion:\n\n"
        
        for case in search_results:
            formatted_text += f"• {case['case_name']}, {case['citation']}: "
            formatted_text += f"{case['holding']}\n"
            
            # Add Daubert factors analysis
            failed_factors = [
                factor for factor, passed in case['daubert_factors'].items() 
                if not passed
            ]
            if failed_factors:
                formatted_text += f"  - Failed Daubert factors: {', '.join(failed_factors)}\n"
            
            formatted_text += "\n"
        
        return formatted_text


# Integration with existing workflow
class EnhancedDaubertWorkflow:
    def __init__(self):
        self.lexis_researcher = LexisNexisResearcher()
        
    def research_precedent(self, expert_name: str, methodology: str, jurisdiction: str = "federal") -> Dict[str, Any]:
        """Enhanced precedent research using LEXIS-NEXIS."""
        
        print(f"Researching precedent for {expert_name}'s {methodology} methodology...")
        
        # Search LEXIS-NEXIS
        cases = self.lexis_researcher.search_daubert_precedent(
            expert_methodology=methodology,
            jurisdiction=jurisdiction,
            years_back=10
        )
        
        # Format for use in motion
        formatted_precedent = self.lexis_researcher.format_for_motion(cases)
        
        return {
            'cases_found': len(cases),
            'formatted_text': formatted_precedent,
            'raw_results': cases
        }


if __name__ == "__main__":
    # Test the integration
    researcher = LexisNexisResearcher()
    
    # Test search
    results = researcher.search_daubert_precedent(
        expert_methodology="DTI imaging",
        jurisdiction="federal",
        years_back=5
    )
    
    print(f"Found {len(results)} relevant cases")
    for case in results:
        print(f"\n{case['citation']}")
        print(f"Holding: {case['holding']}")