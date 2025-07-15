#!/usr/bin/env python3
"""
Dify workflow configuration for LEXICON MVP
Implements the 4-node chain for Daubert motion generation
"""

import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv
from lexis_nexis_integration import LexisNexisResearcher

load_dotenv()


class DifyWorkflow:
    def __init__(self):
        self.api_key = os.getenv("DIFY_API_KEY")
        self.api_url = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.lexis_researcher = LexisNexisResearcher()
        
    def create_daubert_workflow(self) -> Dict[str, Any]:
        """Create the Daubert motion workflow in Dify."""
        workflow_config = {
            "name": "LEXICON Legal Motion Generator",
            "description": "Multi-step workflow for generating Daubert motions, other motions in limine, and oppositions to MIL",
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "data": {
                        "variables": [
                            {
                                "name": "brief_type",
                                "type": "select",
                                "required": True,
                                "description": "Type of motion to generate",
                                "options": [
                                    "Daubert motion",
                                    "Other motions in limine",
                                    "Opposition to MIL"
                                ]
                            },
                            {
                                "name": "expert_name",
                                "type": "string",
                                "required": True,
                                "description": "Name of the expert witness",
                                "max_length": 100
                            },
                            {
                                "name": "case_file_list",
                                "type": "string",
                                "required": False,
                                "description": "Optional list of specific case files to search",
                                "max_length": 500
                            },
                            {
                                "name": "user_ID",
                                "type": "string",
                                "required": True,
                                "description": "LEXIS-NEXIS username for database access",
                                "max_length": 50
                            },
                            {
                                "name": "database_password",
                                "type": "password",
                                "required": True,
                                "description": "LEXIS-NEXIS password for secure access",
                                "max_length": 100
                            },
                            {
                                "name": "jurisdiction",
                                "type": "select",
                                "required": True,
                                "description": "Jurisdiction for legal precedent research",
                                "multiple": True,
                                "options": [
                                    "Indiana",
                                    "Illinois"
                                ]
                            }
                        ]
                    }
                },
                {
                    "id": "extraction_and_analysis",
                    "type": "llm",
                    "data": {
                        "model": "o3-pro-2025-06-10",
                        "reasoning_effort": "high",
                        "response_format": "text",
                        "temperature": 0.3,
                        "max_tokens": 8000,
                        "top_p": 0.95,
                        "context": "{inputs.case_file_list}",
                        "knowledge_retrieval": {
                            "enabled": True,
                            "knowledge_base": "case_file_{inputs.user_ID}",
                            "query": "{inputs.expert_name}",
                            "retrieval_mode": "multiple_retrieval",
                            "top_k": 30,
                            "score_threshold": 0.65,
                            "reranking_model": "rerank-2"
                        },
                        "prompt": """You are an AI Legal Analyst specializing in the critical evaluation of expert witness testimony for litigation. Your purpose is to conduct a deep, multi-document analysis of an expert witness and their stated opinions. You must be meticulous, objective, and structure your output for immediate use by a trial attorney.

Your analysis will be based on the provided {{#context#}} case files (which may include expert reports, deposition transcripts, CVs, scientific articles, etc.).

**Primary Objective:** Deconstruct the testimony of **Expert Name: {{inputs.expert_name}}** in **Jurisdiction: {{inputs.jurisdiction}}**

**Output Formatting:**
- Use Markdown for all formatting
- Use `#` for main title, `##` for major sections, `###` for sub-sections
- Use bolding (`**text**`) for key terms and direct quotes
- Use bullet points (`-`) for lists of findings
- Include page/line citations in format: `[Report p.12]` or `[Depo 45:12-18]`
- Begin with `## 🚨 CRITICAL FLAGS SUMMARY 🚨` listing top 3-5 vulnerabilities

---

{% if inputs.brief_type == "Daubert motion" %}
# Daubert Motion Analysis: Expert {{inputs.expert_name}}

## 🚨 CRITICAL FLAGS SUMMARY 🚨
- [Synthesize the most damaging vulnerabilities found across all categories below]

## I. Expert Qualifications & Potential Bias
- **Prior Testimony History:** List all known prior cases, noting party represented
- **Prior Challenges:** Any Daubert challenges or exclusions with court holdings
- **Financial Bias:** Fee structure, % income from litigation, repeat business
- **CV Inconsistencies:** Discrepancies between CV and deposition testimony

## II. Opinion & Methodology Deconstruction (Daubert Factors)

### A. Summary of Stated Opinions
- Extract each distinct opinion with direct quotes
- Identify "fit" language connecting opinion to case facts

### B. Factor 1: Testability / Falsifiability
- **Stated Methodology:** Quote step-by-step description
- **Hypothesis:** Is core hypothesis explicitly stated and falsifiable?
- **Assumptions:** List all key assumptions with citations

### C. Factor 2: Peer Review & Publication
- **Supporting Literature:** Key peer-reviewed articles cited
- **Contradictory Literature:** Studies that challenge methodology
- **Self-Citation:** Frequency and concern level
- **Litigation Science:** Is method primarily used in court vs. clinical practice?

### D. Factor 3: Known or Potential Error Rate
- **Stated Error Rate:** Quote any numerical/qualitative error rates
- **Missing Error Rate:** If absent, state: **"Expert failed to provide error rate"**
- **Accuracy Variables:** Factors expert admits affect accuracy

### E. Factor 4: Standards & Controls
- **Governing Standards:** Industry/professional standards (ASTM, ISO, etc.)
- **Deviations:** Compare methodology to standards, note deviations

### F. Factor 5: General Acceptance
- **Claims of Acceptance:** Quote "generally accepted" claims
- **Limited Acceptance Evidence:** Novel, controversial, or minority view indicators

### G. Temporal Analysis
- **Testing Timeline:** When performed relative to injury
- **Opinion Evolution:** Changes from report to deposition
- **Critical Gaps:** Missing time periods in records

## III. Cross-Document Contradictions
- **Report vs. Deposition:** Side-by-side contradictions
- **Fact Conflicts:** Where assumptions contradict case facts

## IV. {{inputs.jurisdiction}} Specific Considerations
- **Legal Standard:** [Daubert/Frye requirements in jurisdiction]
- **Key State Precedents:** Relevant admissibility cases
- **Local Rules:** Special expert disclosure requirements

{% elif inputs.brief_type == "Other motions in limine" %}
# Motion In Limine Analysis: Expert {{inputs.expert_name}}

## 🚨 CRITICAL FLAGS SUMMARY 🚨
- [Synthesize most significant relevance/prejudice concerns]

## I. Relevance Analysis (FRE 401 & 402)
- **Case Fact Connection:** How each opinion relates to disputed facts
- **Legal Conclusion Risk:** Opinions that invade jury's province

## II. Unfair Prejudice & Confusion (FRE 403)
- **Inflammatory Language:** Emotionally charged statements
- **Jury Confusion Risk:** Topics within common understanding
- **403 Balancing:** Probative value vs. prejudicial effect

## III. Qualifications & Scope
- **Opinion-Specific Credentials:** Match each opinion to expertise
- **Proposed Testimony Limits:** Bulleted scope restrictions

## IV. {{inputs.jurisdiction}} Specific Standards
- **State Evidence Rules:** Deviations from federal rules
- **Precedent on Scope:** State cases limiting expert testimony

{% elif inputs.brief_type == "Opposition to MIL" %}
# Opposition to Motion in Limine: Defending {{inputs.expert_name}}

## 🚨 KEY STRENGTHS SUMMARY 🚨
- [Highlight strongest defensible aspects]

## I. Methodology Validation
- **Scientific Support:** Peer-reviewed validation
- **Acceptable Error Rates:** Context showing reliability
- **Standards Compliance:** Adherence to professional standards

## II. Qualifications & Fit
- **Opinion-Specific Expertise:** CV support for each opinion
- **Jury Assistance:** How testimony clarifies complex evidence

## III. Preemptive Rebuttals
- **"Novel Method" Defense:** Evidence of established use
- **"Biased Expert" Defense:** Balanced testimony history
- **"Lack of Fit" Defense:** Clear connection to case facts

## IV. {{inputs.jurisdiction}} Supportive Precedent
- **Favorable Admissibility Rulings:** Similar experts/methods admitted
- **Liberal Admission Standard:** State preference for jury consideration

{% endif %}

## V. Trial Strategy Implications
- **Key Cross-Examination Themes:** Top 3 attack vectors
- **Demonstrative Evidence Vulnerabilities:** Visual aids that expose flaws
- **LEXIS-NEXIS Research Priorities:** Specific searches needed for precedent

---
**Analysis Complete**"""
                    }
                },
   - Equipment or software used
   - Any deviations from standard procedures
   - Missing tests that would typically be performed

3. **Qualifications & Credentials**
   - Education and degrees
   - Board certifications (current vs lapsed)
   - Relevant experience with the specific condition/injury
   - Publications on the topic
   - Frequency of testimony (professional witness indicators)

4. **Scientific Basis**
   - Studies or literature cited
   - Whether cited studies actually support their conclusions
   - Peer review status of methods
   - Known error rates mentioned

5. **Red Flags for Challenge**
   - Conclusions that exceed the data
   - Selective use of test results
   - Ignored alternative explanations
   - Temporal inconsistencies
   - Missing foundation for opinions

For {inputs.brief_type}, pay special attention to:
- If Daubert: Focus on methodology reliability and scientific validity
- If Other MIL: Focus on relevance and potential prejudice
- If Opposition: Focus on defending methodology and qualifications

Format findings in detailed bullet points with specific quotes and page references where available."""
                    }
                },
                {
                    "id": "find_contradictions",
                    "type": "knowledge_retrieval",
                    "data": {
                        "knowledge_base": "case_file",
                        "prompt": """Review the deposition transcripts and medical records. Identify:
1. Any facts, statements, or omissions that contradict the conclusions from: {extract_opinions.output}
2. Inconsistencies in the expert's testimony vs. their report
3. Missing or incomplete medical history considerations
4. Alternative explanations not addressed by the expert

Provide specific quotes with page/line references where possible."""
                    }
                },
                {
                    "id": "find_precedent",
                    "type": "knowledge_retrieval",
                    "data": {
                        "knowledge_base": "precedent_tbi_daubert",
                        "prompt": """Based on the expert's methodologies from: {extract_opinions.output}

Search for legal precedent that:
1. Questions the reliability of these specific methods under Daubert
2. Addresses issues with:
   - Testability and falsifiability
   - Peer review and publication
   - Known or potential error rates
   - General acceptance in the field
3. Specifically focuses on TBI/DTI imaging reliability challenges

Cite specific cases with holdings and page numbers.

ADDITIONAL LEXIS-NEXIS PRECEDENT:
{inputs.additional_precedent}"""
                    }
                },
                {
                    "id": "draft_argument",
                    "type": "llm",
                    "data": {
                        "model": "gpt-4",
                        "prompt": """Synthesize all information to draft the 'Argument' section of a Daubert motion.

Expert opinions: {extract_opinions.output}
Contradictions found: {find_contradictions.output}
Legal precedent: {find_precedent.output}

Structure the argument as follows:

I. INTRODUCTION
[Brief overview of why expert should be excluded]

II. THE EXPERT'S UNRELIABLE METHODOLOGY
[For each methodology, explain why it fails Daubert]

III. CONTRADICTIONS WITH CASE FACTS
[Detail specific contradictions with evidence]

IV. LEGAL PRECEDENT MANDATES EXCLUSION
[Apply precedent to this expert's specific failings]

V. CONCLUSION
[Summarize why exclusion is required]

Use formal legal writing style with proper citations."""
                    }
                },
                {
                    "id": "end",
                    "type": "end",
                    "data": {
                        "outputs": [
                            {
                                "name": "motion_text",
                                "value": "{draft_argument.output}"
                            }
                        ]
                    }
                }
            ]
        }
        
        return workflow_config
    
    def execute_workflow(self, expert_name: str, use_lexis_nexis: bool = True) -> str:
        """Execute the Daubert workflow for a specific expert."""
        endpoint = f"{self.api_url}/workflows/run"
        
        # If using LEXIS-NEXIS, enhance the workflow inputs
        additional_context = ""
        if use_lexis_nexis:
            additional_context = self._get_lexis_nexis_context(expert_name)
        
        payload = {
            "workflow_id": "daubert_motion_generator",
            "inputs": {
                "expert_name": expert_name,
                "additional_precedent": additional_context
            }
        }
        
        response = requests.post(endpoint, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("outputs", {}).get("motion_text", "")
        else:
            raise Exception(f"Workflow execution failed: {response.text}")
    
    def _get_lexis_nexis_context(self, expert_name: str) -> str:
        """Get relevant precedent from LEXIS-NEXIS based on expert's methodology."""
        
        # For demo, we'll search for common TBI methodologies
        # In production, this would extract methodology from the expert's report
        methodologies = ["DTI imaging", "neuropsychological testing", "biomechanical analysis"]
        
        all_precedent = []
        for methodology in methodologies:
            try:
                results = self.lexis_researcher.search_daubert_precedent(
                    expert_methodology=methodology,
                    jurisdiction="federal",
                    years_back=10
                )
                if results:
                    formatted = self.lexis_researcher.format_for_motion(results[:3])  # Top 3 cases
                    all_precedent.append(f"\n{methodology.upper()} PRECEDENT:\n{formatted}")
            except Exception as e:
                print(f"Error searching for {methodology}: {str(e)}")
        
        return "\n".join(all_precedent) if all_precedent else ""


    def execute_advanced_workflow(self, expert_name: str, expert_report_path: str = None) -> Dict[str, Any]:
        """
        Execute advanced workflow with intelligent LEXIS-NEXIS integration.
        
        Args:
            expert_name: Name of the expert witness
            expert_report_path: Path to the expert's report for methodology extraction
            
        Returns:
            Complete motion with enhanced precedent research
        """
        
        # Extract methodologies from expert report if provided
        methodologies = []
        if expert_report_path and os.path.exists(expert_report_path):
            methodologies = self._extract_methodologies_from_report(expert_report_path)
        
        # Search LEXIS-NEXIS for each identified methodology
        precedent_sections = []
        for methodology in methodologies:
            print(f"Searching LEXIS-NEXIS for precedent on: {methodology}")
            
            results = self.lexis_researcher.search_daubert_precedent(
                expert_methodology=methodology,
                jurisdiction="federal",  # Could be parameterized
                years_back=10
            )
            
            if results:
                formatted = self.lexis_researcher.format_for_motion(results[:5])
                precedent_sections.append(f"\n{methodology.upper()} CHALLENGES:\n{formatted}")
        
        # Execute workflow with enhanced context
        enhanced_context = "\n".join(precedent_sections)
        
        return {
            "motion_text": self.execute_workflow(expert_name, use_lexis_nexis=False),
            "lexis_nexis_precedent": enhanced_context,
            "methodologies_identified": methodologies,
            "cases_found": len(precedent_sections)
        }
    
    def _extract_methodologies_from_report(self, report_path: str) -> List[str]:
        """Extract testing methodologies from expert report."""
        
        # Common TBI assessment methodologies to look for
        methodology_patterns = {
            'dti': ['diffusion tensor imaging', 'dti', 'fractional anisotropy', 'white matter tract'],
            'neuropsych': ['neuropsychological', 'cognitive testing', 'wais', 'trails', 'wisconsin card'],
            'biomechanical': ['biomechanical', 'force analysis', 'acceleration', 'injury threshold'],
            'imaging': ['mri', 'ct scan', 'pet scan', 'spect', 'brain imaging'],
            'vestibular': ['vestibular', 'balance testing', 'videonystagmography', 'vng'],
            'qeeg': ['qeeg', 'quantitative eeg', 'brain mapping', 'electroencephalography']
        }
        
        methodologies_found = []
        
        # Read the report
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                report_text = f.read().lower()
            
            # Search for each methodology pattern
            for method_name, patterns in methodology_patterns.items():
                for pattern in patterns:
                    if pattern in report_text:
                        if method_name == 'dti':
                            methodologies_found.append('DTI imaging')
                        elif method_name == 'neuropsych':
                            methodologies_found.append('neuropsychological testing')
                        elif method_name == 'biomechanical':
                            methodologies_found.append('biomechanical analysis')
                        else:
                            methodologies_found.append(method_name)
                        break
            
        except Exception as e:
            print(f"Error reading expert report: {str(e)}")
        
        return list(set(methodologies_found))  # Remove duplicates


if __name__ == "__main__":
    # Test workflow creation
    workflow = DifyWorkflow()
    config = workflow.create_daubert_workflow()
    print("Workflow configuration created successfully")
    
    # Test LEXIS-NEXIS integration
    print("\nTesting LEXIS-NEXIS integration...")
    lexis_context = workflow._get_lexis_nexis_context("Dr. Test Expert")
    print(f"Retrieved precedent context: {len(lexis_context)} characters")