#!/usr/bin/env python3
"""
Simplified Dify workflow for LEXICON MVP
Focuses on Daubert motion generation without complexity
"""

import os
import requests
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class SimplifiedLEXICONWorkflow:
    def __init__(self):
        self.dify_api_key = os.getenv('DIFY_API_KEY')
        self.dify_base_url = os.getenv('DIFY_API_URL', 'http://localhost/v1')
        
    def process_for_daubert(self, expert_name: str, deposition_text: str, case_context: str = "") -> Dict[str, Any]:
        """
        Simplified workflow: Extract → Analyze → Draft
        No loops, no complex agents, just get it done
        """
        
        # Step 1: Extract key expert opinions
        expert_opinions = self._extract_expert_opinions(expert_name, deposition_text)
        
        # Step 2: Find weaknesses (no external search for MVP)
        weaknesses = self._analyze_weaknesses(expert_opinions, deposition_text)
        
        # Step 3: Draft the motion
        motion_text = self._draft_daubert_motion(
            expert_name=expert_name,
            expert_opinions=expert_opinions,
            weaknesses=weaknesses,
            case_context=case_context
        )
        
        return {
            'expert_name': expert_name,
            'extracted_opinions': expert_opinions,
            'identified_weaknesses': weaknesses,
            'motion_text': motion_text
        }
        
    def _extract_expert_opinions(self, expert_name: str, deposition_text: str) -> str:
        """Extract expert's key opinions and methodologies"""
        
        prompt = f"""You are a senior paralegal analyzing expert testimony.
        
Expert: {expert_name}
Deposition Text: {deposition_text[:3000]}...

Extract:
1. Expert's primary conclusions (numbered list)
2. Methodologies used
3. Key admissions or problematic statements

Format as structured text for legal use."""

        # For MVP, we'll use a simple API call
        # In production, this would call your Dify workflow
        response = self._call_llm(prompt)
        return response
        
    def _analyze_weaknesses(self, expert_opinions: str, deposition_text: str) -> str:
        """Identify Daubert vulnerabilities"""
        
        prompt = f"""You are an experienced litigator preparing a Daubert challenge.

Expert Opinions:
{expert_opinions}

Full Deposition:
{deposition_text[:2000]}...

Identify weaknesses under Daubert factors:
1. Testability - Can the theory be tested?
2. Peer Review - Has it been peer-reviewed?
3. Error Rate - Known error rates?
4. Standards - Are there standards controlling the technique?
5. General Acceptance - Is it generally accepted?

Focus on TBI-specific issues like DTI reliability."""

        response = self._call_llm(prompt)
        return response
        
    def _draft_daubert_motion(self, expert_name: str, expert_opinions: str, 
                             weaknesses: str, case_context: str) -> str:
        """Draft the core argument section"""
        
        prompt = f"""You are drafting a Daubert motion to exclude {expert_name}'s testimony.

Expert's Opinions:
{expert_opinions}

Identified Weaknesses:
{weaknesses}

Case Context:
{case_context}

Draft the "Argument" section of a Daubert motion. Structure:

I. {expert_name}'s Methodology Fails Daubert's Reliability Standards
   A. [First major weakness]
   B. [Second major weakness]
   
II. The Expert's Opinions Lack Scientific Foundation
   A. [Specific opinion critique]
   B. [Methodology problems]

III. Conclusion

Use persuasive legal writing. Cite Daubert v. Merrell Dow and relevant TBI cases."""

        response = self._call_llm(prompt)
        return response
        
    def _call_llm(self, prompt: str, model: str = "gpt-4") -> str:
        """Simple LLM call - replace with your Dify API call"""
        
        # For testing without Dify running:
        if not self.dify_api_key:
            return f"[MOCK RESPONSE FOR: {prompt[:50]}...]"
            
        # Real Dify API call would go here
        headers = {
            'Authorization': f'Bearer {self.dify_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'inputs': {'query': prompt},
            'response_mode': 'blocking',
            'user': 'lexicon-mvp'
        }
        
        try:
            response = requests.post(
                f'{self.dify_base_url}/chat-messages',
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json().get('answer', 'No response')
            else:
                return f"API Error: {response.status_code}"
        except Exception as e:
            return f"Error calling API: {str(e)}"


# Quick test
if __name__ == "__main__":
    workflow = SimplifiedLEXICONWorkflow()
    
    # Test with sample data
    result = workflow.process_for_daubert(
        expert_name="Dr. Smith",
        deposition_text="Q: What methodology did you use? A: I used DTI imaging...",
        case_context="Motor vehicle accident, mild TBI claim"
    )
    
    print(json.dumps(result, indent=2))
