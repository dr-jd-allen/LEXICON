#!/usr/bin/env python3
"""
Dify workflow configuration for LEXICON MVP
Implements the complete chain for Daubert/Frye motion generation
Clean version with all syntax fixes and complete node configurations
"""

import os
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv
from lexis_nexis_integration import LexisNexisResearcher

load_dotenv()


class DifyWorkflow:
    def __init__(self):
        self.api_key = os.getenv("DIFY_API_KEY", "app-Vi34f3f0sN76CXD2LnTQ0p0T")
        self.api_url = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.lexis_researcher = LexisNexisResearcher()
        
    def create_daubert_workflow(self) -> Dict[str, Any]:
        """Create the Daubert motion workflow in Dify."""
        workflow_config = {
            "name": "LEXICON: Legal Expertise with Contextual Intelligence",
            "description": "Multi-step agentic AI workflow for generating Daubert/Frye motions, other motions in limine (MIL), and oppositions to MIL",
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "data": {
                        "variables": [
                            {
                                "name": "brief_type",
                                "field_type": "select",
                                "required": True,
                                "description": "Type of motion to generate:",
                                "options": [
                                    "Daubert/Frye motion",
                                    "Other motions in limine",
                                    "Opposition to MIL"
                                ]
                            },
                            {
                                "name": "expert_name",
                                "field_type": "text-input",
                                "required": True,
                                "description": "Name of the expert witness:",
                                "max_length": 100
                            },
                            {
                                "name": "case_file_list",
                                "field_type": "file",
                                "required": True,
                                "description": "Specific case files uploaded by user to search:",
                                "max_file_size": "15",
                                "allowed_file_types": [".pdf", ".txt", ".docx"],
                                "allowed_file_extensions": ["pdf", "txt", "docx"],
                                "allowed_file_upload_methods": ["local_file", "remote_url"]
                            },
                            {
                                "name": "user_ID",
                                "field_type": "text-input",
                                "required": True,
                                "description": "LEXIS-NEXIS username for database access:",
                                "default": "Brown, Robert4",
                                "max_length": 50
                            },
                            {
                                "name": "database_password",
                                "field_type": "text-input",
                                "required": True,
                                "description": "LEXIS-NEXIS password for secure access:",
                                "default": "baileYI",
                                "max_length": 50
                            },
                            {
                                "name": "jurisdiction",
                                "field_type": "select",
                                "required": True,
                                "description": "Jurisdiction:",
                                "multiple": True,
                                "options": [
                                    "Indiana",
                                    "Illinois",
                                    "Federal"
                                ]
                            }
                        ]
                    }
                },
                {
                    "id": "research_agent",
                    "type": "llm",
                    "data": {
                        "model": {
                            "provider": "openai",
                            "name": "o3-deep-research-2025-06-26",
                            "mode": "chat",
                            "completion_params": {
                                "temperature": 0.7,
                                "top_p": 0.95,
                                "max_tokens": 10000,
                                "presence_penalty": 0,
                                "frequency_penalty": 0,
                                "reasoning_effort": "high",
                                "extended_thinking": True
                            }
                        },
                        "tools": [
                            {
                                "type": "web_search",
                                "enabled": True,
                                "config": {
                                    "search_query_template": "{{inputs.expert_name}} expert witness testimony Daubert Frye challenges"
                                }
                            },
                            {
                                "type": "knowledge_retrieval",
                                "enabled": True,
                                "config": {
                                    "knowledge_base": "case_file_{{inputs.user_ID}}",
                                    "query": "{{inputs.expert_name}}",
                                    "retrieval_mode": "multiple_retrieval",
                                    "top_k": 30,
                                    "score_threshold": 0.65,
                                    "reranking_model": "rerank-2"
                                }
                            }
                        ],
                        "context": "{{inputs.case_file_list}}",
                        "prompt": """You are an AI Legal Analyst specializing in the critical evaluation of expert witness testimony for litigation. Your purpose is to conduct a deep, multi-document analysis of an expert witness and their stated opinions. You must be meticulous, objective, and structure your output for immediate use by a trial attorney.

Your analysis will be based on the provided {{#context#}} case files (which may include expert reports, deposition transcripts, CVs, scientific articles, etc.).

**Primary Objective:** Deconstruct the testimony of **Expert Name: {{inputs.expert_name}}** in **Jurisdiction: {{inputs.jurisdiction}}**

**Output Formatting:**
- Use Markdown for all document formatting
- Adhere to the latest version of MLA style for citations, page numbering, etc.
- Use `#` for main title, `##` for major sections, `###` for sub-sections
- Use bolding (`**text**`) for key terms and italics (*text*) for direct quotes
- Use bullet points (`-`) for lists of findings
- Include page/line citations in format: `[Report p.12]` or `[Depo 45:12-18]`
- Begin with `## 🚨 CRITICAL FLAGS SUMMARY 🚨` listing top 3-5 vulnerabilities

---

{% if inputs.brief_type == "Daubert/Frye motion" %}
# Daubert/Frye Motion Analysis: Expert {{inputs.expert_name}}

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
                {
                    "id": "find_contradictions",
                    "type": "llm",
                    "data": {
                        "model": {
                            "provider": "openai",
                            "name": "gpt-4-turbo-preview",
                            "mode": "chat",
                            "completion_params": {
                                "temperature": 0.2,
                                "top_p": 0.9,
                                "max_tokens": 4000
                            }
                        },
                        "tools": [
                            {
                                "type": "knowledge_retrieval",
                                "enabled": True,
                                "config": {
                                    "knowledge_base": "case_file_{{inputs.user_ID}}",
                                    "query": "{{research_agent.output}}",
                                    "retrieval_mode": "multiple_retrieval",
                                    "top_k": 20,
                                    "score_threshold": 0.7,
                                    "reranking_model": "rerank-2"
                                }
                            }
                        ],
                        "context": "{{research_agent.output}}",
                        "prompt": """You are a forensic legal analyst specializing in finding contradictions and inconsistencies in expert testimony.

**Input from Previous Analysis:**
{{research_agent.output}}

**Your Task:** Search through the case file knowledge base for contradictions, inconsistencies, and omissions that undermine the expert's opinions.

**Focus Areas:**

1. **Internal Contradictions**
   - Expert report vs. deposition testimony
   - Earlier statements vs. later statements
   - CV claims vs. actual testimony

2. **Factual Contradictions**
   - Expert assumptions vs. case facts
   - Timeline conflicts
   - Medical history discrepancies

3. **Methodological Inconsistencies**
   - Stated methodology vs. actual procedures
   - Cherry-picked data or tests
   - Ignored negative findings

4. **Omissions**
   - Missing differential diagnoses
   - Unconsidered alternative causes
   - Ignored confounding factors

**Output Format:**
## 🚨 CONTRADICTION SUMMARY

### Critical Contradictions
[List top 3-5 most damaging contradictions]

### Detailed Findings

#### 1. [Contradiction Type]
- **What Expert Stated:** [Quote with citation]
- **Contradicting Evidence:** [Quote with citation]
- **Impact:** [How this undermines the opinion]

[Continue for each contradiction found]

### Missing Considerations
- [List key factors the expert failed to address]

**Search the knowledge base thoroughly for any evidence that contradicts or undermines the expert's positions identified in the previous analysis.**"""
                    }
                },
                {
                    "id": "find_precedent",
                    "type": "llm",
                    "data": {
                        "model": {
                            "provider": "openai",
                            "name": "gpt-4-turbo-preview",
                            "mode": "chat",
                            "completion_params": {
                                "temperature": 0.3,
                                "top_p": 0.95,
                                "max_tokens": 6000
                            }
                        },
                        "tools": [
                            {
                                "type": "api_request",
                                "enabled": True,
                                "config": {
                                    "method": "POST",
                                    "url": "{{env.LEXIS_NEXIS_API_URL}}/search",
                                    "headers": {
                                        "Authorization": "Basic {{inputs.user_ID}}:{{inputs.database_password}}",
                                        "Content-Type": "application/json"
                                    },
                                    "body": {
                                        "query": "{{research_agent.output}}",
                                        "jurisdiction": "{{inputs.jurisdiction}}",
                                        "practice_area": "expert_witness_challenges",
                                        "date_range": "last_10_years"
                                    }
                                }
                            }
                        ],
                        "context": "{{research_agent.output}}\n\n{{find_contradictions.output}}",
                        "prompt": """You are a legal research specialist focusing on finding precedent that supports challenging expert witness testimony.

**Expert Analysis Summary:**
{{research_agent.output}}

**Contradictions Found:**
{{find_contradictions.output}}

**Your Task:** Search LEXIS-NEXIS and other legal databases for precedent cases that:

1. **Challenge Similar Methodologies**
   - Cases excluding experts using similar techniques
   - Rulings on specific Daubert/Frye factors
   - Appellate decisions on methodology reliability

2. **Address Expert Qualifications**
   - Cases limiting expert testimony scope
   - Rulings on "professional witness" bias
   - Decisions on expertise-opinion mismatch

3. **Support Exclusion Arguments**
   - Precedent on lack of fit to case facts
   - Rulings on speculative opinions
   - Cases excluding cumulative expert testimony

**Search Parameters:**
- **Jurisdictions:** {{inputs.jurisdiction}} (prioritize), Federal courts, persuasive authority
- **Time Frame:** Last 10 years (prioritize recent decisions)
- **Keywords:** Based on specific methodologies and issues identified

**Output Format:**

## LEGAL PRECEDENT SUPPORTING EXCLUSION

### Directly On-Point Cases

#### [Case Name, Citation, Year]
- **Court:** [Jurisdiction and level]
- **Holding:** [Key ruling on expert admissibility]
- **Relevant Quote:** "[Direct quote from opinion]"
- **Application:** [How this applies to current expert]

### Methodology-Specific Precedent

#### [Methodology Type] Challenges
[List cases challenging this specific methodology]

### Persuasive Authority
[Cases from other jurisdictions that may be persuasive]

### Strategic Citations
- **Strongest Precedent:** [Top 3 cases to lead with]
- **Distinguish Opposition Cases:** [Anticipated cases opposition may cite]

**Focus on finding the most recent and directly applicable precedent from the specified jurisdictions.**"""
                    }
                },
                {
                    "id": "draft_argument",
                    "type": "llm",
                    "data": {
                        "model": {
                            "provider": "openai",
                            "name": "gpt-4-turbo-preview",
                            "mode": "chat",
                            "completion_params": {
                                "temperature": 0.4,
                                "top_p": 0.95,
                                "max_tokens": 8000
                            }
                        },
                        "context": "{{research_agent.output}}\n\n{{find_contradictions.output}}\n\n{{find_precedent.output}}",
                        "prompt": """You are a senior litigation attorney drafting the argument section of a {{inputs.brief_type}}.

**Comprehensive Analysis:**
- Expert Analysis: {{research_agent.output}}
- Contradictions: {{find_contradictions.output}}
- Legal Precedent: {{find_precedent.output}}

**Draft Requirements:**
1. Use formal legal writing style
2. Apply MLA citation format for all references
3. Structure arguments from strongest to weakest
4. Anticipate and address counterarguments
5. Use persuasive language appropriate for judicial audience

**Argument Structure:**

{% if inputs.brief_type == "Daubert/Frye motion" %}

## ARGUMENT

### I. INTRODUCTION
[2-3 paragraphs setting up why exclusion is warranted]

### II. [EXPERT NAME]'S OPINIONS FAIL THE DAUBERT/FRYE STANDARD

#### A. The Methodology Lacks Scientific Reliability
[Address each Daubert factor with specific examples]

#### B. The Expert's Qualifications Do Not Match the Proffered Opinions
[Detail mismatches between expertise and testimony]

#### C. The Opinions Do Not "Fit" the Facts of This Case
[Explain disconnect between opinions and case facts]

### III. THE EXPERT'S TESTIMONY CONTAINS FATAL CONTRADICTIONS
[Detail key contradictions with evidence citations]

### IV. ESTABLISHED PRECEDENT MANDATES EXCLUSION

#### A. This Court Has Previously Excluded Similar Testimony
[Cite local precedent]

#### B. Courts Nationwide Reject Such Methodologies
[Cite persuasive authority]

### V. THE PROBATIVE VALUE IS SUBSTANTIALLY OUTWEIGHED BY THE DANGER OF UNFAIR PREJUDICE
[403 balancing analysis if applicable]

### VI. CONCLUSION
[Strong closing arguing for complete exclusion]

{% elif inputs.brief_type == "Other motions in limine" %}

## ARGUMENT

### I. INTRODUCTION
[Set up specific prejudice/relevance concerns]

### II. THE EXPERT'S TESTIMONY EXCEEDS PERMISSIBLE BOUNDS

#### A. Irrelevant Opinions Should Be Excluded
[FRE 401/402 analysis]

#### B. The Testimony Will Confuse and Mislead the Jury
[FRE 403 analysis]

### III. LIMITING INSTRUCTIONS CANNOT CURE THE PREJUDICE
[Explain why partial exclusion insufficient]

### IV. CONCLUSION
[Request specific relief]

{% elif inputs.brief_type == "Opposition to MIL" %}

## ARGUMENT

### I. INTRODUCTION
[Frame expert's importance to case]

### II. THE EXPERT'S METHODOLOGY SATISFIES ALL RELIABILITY REQUIREMENTS

#### A. The Techniques Are Scientifically Valid
[Address each Daubert factor favorably]

#### B. The Expert Is Highly Qualified
[Detail credentials and experience]

### III. THE TESTIMONY WILL ASSIST THE TRIER OF FACT
[Explain complexity requiring expert guidance]

### IV. THE MOTION'S CRITICISMS GO TO WEIGHT, NOT ADMISSIBILITY
[Argue cross-examination is proper remedy]

### V. PRECEDENT SUPPORTS ADMISSION
[Cite favorable cases]

### VI. CONCLUSION
[Argue for denial of motion]

{% endif %}

**Remember:**
- Every assertion must have evidentiary support
- Use persuasive transitions between arguments
- Maintain professional tone throughout
- End with specific relief requested"""
                    }
                },
                {
                    "id": "end",
                    "type": "end",
                    "data": {
                        "outputs": [
                            {
                                "name": "motion_text",
                                "type": "text",
                                "value": "{{draft_argument.output}}"
                            },
                            {
                                "name": "analysis_summary",
                                "type": "text",
                                "value": "{{research_agent.output}}"
                            },
                            {
                                "name": "contradictions_found",
                                "type": "text",
                                "value": "{{find_contradictions.output}}"
                            },
                            {
                                "name": "precedent_research",
                                "type": "text",
                                "value": "{{find_precedent.output}}"
                            }
                        ]
                    }
                }
            ],
            "edges": [
                {
                    "id": "start-to-research",
                    "source": "start",
                    "target": "research_agent"
                },
                {
                    "id": "research-to-contradictions",
                    "source": "research_agent",
                    "target": "find_contradictions"
                },
                {
                    "id": "contradictions-to-precedent",
                    "source": "find_contradictions",
                    "target": "find_precedent"
                },
                {
                    "id": "precedent-to-draft",
                    "source": "find_precedent",
                    "target": "draft_argument"
                },
                {
                    "id": "draft-to-end",
                    "source": "draft_argument",
                    "target": "end"
                }
            ]
        }
        
        return workflow_config
    
    def execute_workflow(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Daubert workflow with provided inputs."""
        endpoint = f"{self.api_url}/workflows/run"
        
        # Validate required inputs
        required_fields = ["brief_type", "expert_name", "case_file_list", "user_ID", 
                          "database_password", "jurisdiction"]
        for field in required_fields:
            if field not in inputs:
                raise ValueError(f"Missing required input: {field}")
        
        payload = {
            "workflow_id": "lexicon_daubert_workflow",
            "inputs": inputs,
            "response_mode": "blocking",  # Wait for completion
            "user": inputs.get("user_ID", "default_user")
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            return {
                "status": "success",
                "outputs": result.get("data", {}).get("outputs", {}),
                "workflow_run_id": result.get("workflow_run_id"),
                "elapsed_time": result.get("elapsed_time")
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e),
                "details": response.text if response else "No response"
            }
    
    def validate_workflow(self) -> Dict[str, Any]:
        """Validate the workflow configuration."""
        config = self.create_daubert_workflow()
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "node_count": len(config.get("nodes", [])),
            "edge_count": len(config.get("edges", []))
        }
        
        # Check nodes
        node_ids = set()
        for node in config.get("nodes", []):
            if "id" not in node:
                validation_results["errors"].append(f"Node missing ID: {node}")
                validation_results["valid"] = False
            else:
                if node["id"] in node_ids:
                    validation_results["errors"].append(f"Duplicate node ID: {node['id']}")
                    validation_results["valid"] = False
                node_ids.add(node["id"])
        
        # Check edges
        for edge in config.get("edges", []):
            if edge.get("source") not in node_ids:
                validation_results["errors"].append(f"Edge source not found: {edge.get('source')}")
                validation_results["valid"] = False
            if edge.get("target") not in node_ids:
                validation_results["errors"].append(f"Edge target not found: {edge.get('target')}")
                validation_results["valid"] = False
        
        # Check for required start and end nodes
        if "start" not in node_ids:
            validation_results["errors"].append("Missing required 'start' node")
            validation_results["valid"] = False
        if "end" not in node_ids:
            validation_results["errors"].append("Missing required 'end' node")
            validation_results["valid"] = False
        
        return validation_results


if __name__ == "__main__":
    # Create workflow instance
    workflow = DifyWorkflow()
    
    # Validate configuration
    print("Validating workflow configuration...")
    validation = workflow.validate_workflow()
    
    if validation["valid"]:
        print("✓ Workflow configuration is valid!")
        print(f"  - {validation['node_count']} nodes")
        print(f"  - {validation['edge_count']} edges")
    else:
        print("✗ Workflow configuration has errors:")
        for error in validation["errors"]:
            print(f"  - {error}")
    
    # Test workflow creation
    config = workflow.create_daubert_workflow()
    print(f"\nWorkflow name: {config['name']}")
    print(f"Total nodes: {len(config['nodes'])}")
    
    # Example execution (commented out to avoid actual API call)
    # inputs = {
    #     "brief_type": "Daubert/Frye motion",
    #     "expert_name": "Dr. John Smith",
    #     "case_file_list": ["expert_report.pdf", "deposition.pdf"],
    #     "user_ID": "Brown, Robert4",
    #     "database_password": "baileYI",
    #     "jurisdiction": ["Illinois", "Federal"]
    # }
    # result = workflow.execute_workflow(inputs)
    # print(f"Execution result: {result}")