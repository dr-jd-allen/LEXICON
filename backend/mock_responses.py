"""
Mock responses for testing LEXICON without API calls
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

class MockResponses:
    """Generate realistic mock responses for testing"""
    
    @staticmethod
    def orchestrator_analysis() -> Dict[str, Any]:
        """Mock Orchestrator (Claude Opus 4) response"""
        return {
            "analysis": {
                "case_type": "Personal Injury - Traumatic Brain Injury",
                "jurisdiction": "State of California",
                "key_facts": [
                    "Plaintiff suffered TBI in automobile accident",
                    "Defendant ran red light at intersection",
                    "Multiple witnesses corroborate plaintiff's account",
                    "Medical records show permanent cognitive impairment"
                ],
                "legal_theories": [
                    "Negligence per se (traffic violation)",
                    "General negligence",
                    "Loss of consortium"
                ],
                "damages_categories": [
                    "Medical expenses (past and future)",
                    "Lost wages and earning capacity",
                    "Pain and suffering",
                    "Loss of enjoyment of life"
                ],
                "strategic_considerations": [
                    "Strong liability case with multiple witnesses",
                    "Focus on long-term impact of TBI",
                    "Consider life care planning expert",
                    "Emphasize defendant's traffic violation history"
                ]
            },
            "confidence": 0.92,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def legal_research() -> Dict[str, Any]:
        """Mock Legal Research Agent (o3-pro) response"""
        cases = [
            {
                "name": "Miller v. Johnson Transportation",
                "citation": "123 Cal.App.4th 456 (2023)",
                "relevance": 0.95,
                "holding": "Traumatic brain injury victims entitled to future medical expenses based on life care plan",
                "facts": "Similar intersection collision with TBI",
                "damages_awarded": "$3.2 million"
            },
            {
                "name": "Smith v. Regional Hospital",
                "citation": "456 F.3d 789 (9th Cir. 2022)",
                "relevance": 0.88,
                "holding": "Expert testimony on TBI long-term effects admissible under Daubert",
                "facts": "Challenge to neuropsychologist expert testimony",
                "key_language": "Courts must recognize evolving understanding of TBI impacts"
            },
            {
                "name": "Davis v. City Transit Authority",
                "citation": "789 Cal.App.4th 123 (2023)",
                "relevance": 0.91,
                "holding": "Lost earning capacity calculations must account for cognitive limitations",
                "facts": "Bus accident resulting in mild TBI",
                "damages_awarded": "$1.8 million"
            }
        ]
        
        return {
            "cases": cases,
            "statutes": [
                {
                    "code": "Cal. Veh. Code § 21453",
                    "title": "Red light violations",
                    "relevance": "Establishes negligence per se"
                }
            ],
            "legal_principles": [
                "Eggshell skull doctrine applies to TBI cases",
                "Future damages must be proven to reasonable medical certainty",
                "Life care plans increasingly accepted for TBI victims"
            ],
            "search_timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def scientific_research() -> Dict[str, Any]:
        """Mock Scientific Research Agent (o4-mini) response"""
        return {
            "medical_literature": [
                {
                    "title": "Long-term cognitive outcomes following moderate to severe TBI",
                    "journal": "Journal of Neurotrauma",
                    "year": 2023,
                    "findings": [
                        "78% of moderate TBI patients show persistent cognitive deficits at 5 years",
                        "Executive function most commonly affected domain",
                        "Early intervention improves outcomes by 35%"
                    ],
                    "pmid": "37654321"
                },
                {
                    "title": "Economic impact of traumatic brain injury: A systematic review",
                    "journal": "Brain Injury",
                    "year": 2024,
                    "findings": [
                        "Average lifetime cost of moderate TBI: $1.2-2.3 million",
                        "Lost productivity accounts for 70% of economic burden",
                        "Vocational rehabilitation reduces long-term costs by 40%"
                    ],
                    "pmid": "38765432"
                }
            ],
            "expert_opinions": [
                {
                    "expert": "Dr. Sarah Mitchell, MD, PhD",
                    "specialty": "Neuropsychology",
                    "institution": "Stanford Medical Center",
                    "opinion": "Modern neuroimaging can objectively demonstrate TBI-related changes"
                }
            ],
            "treatment_protocols": [
                "Comprehensive neuropsychological evaluation recommended",
                "Cognitive rehabilitation therapy shows evidence-based benefits",
                "Multidisciplinary team approach optimal for TBI management"
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def brief_sections() -> Dict[str, Any]:
        """Mock Brief Writer Agent (GPT-4.5) response"""
        return {
            "sections": {
                "introduction": """Plaintiff Jane Doe brings this action seeking compensation for life-altering injuries sustained when Defendant John Smith negligently ran a red light, causing a violent collision that resulted in Ms. Doe suffering a moderate to severe traumatic brain injury. This preventable tragedy has forever changed Ms. Doe's life, robbing her of her cognitive abilities, her career as a software engineer, and her independence.""",
                
                "statement_of_facts": """On March 15, 2023, at approximately 2:30 p.m., Ms. Doe was lawfully proceeding through the intersection of Main Street and First Avenue when Defendant Smith, traveling at excessive speed, ran a red light and struck Ms. Doe's vehicle on the driver's side. The force of impact was so severe that Ms. Doe's vehicle was pushed 50 feet from the point of collision.

Multiple witnesses, including Maria Garcia and Robert Chen, observed Defendant enter the intersection several seconds after the light turned red. Security footage from nearby businesses corroborates these accounts.

Emergency responders found Ms. Doe unconscious at the scene. She was transported to Regional Medical Center where CT scans revealed subdural hematoma and diffuse axonal injury. Ms. Doe remained in a coma for 72 hours and required intensive care for two weeks.""",
                
                "legal_argument": """### I. Defendant's Violation of Vehicle Code § 21453 Constitutes Negligence Per Se

California law is clear: running a red light violates Vehicle Code § 21453 and constitutes negligence per se. See Miller v. Johnson Transportation, 123 Cal.App.4th 456 (2023). Defendant's violation directly caused Plaintiff's injuries.

### II. Plaintiff's Traumatic Brain Injury Entitles Her to Substantial Damages

Recent appellate authority recognizes the devastating long-term impact of TBI. In Miller, the court affirmed a $3.2 million award, noting that "traumatic brain injury victims face a lifetime of challenges requiring comprehensive compensation."

### III. Future Medical Expenses and Lost Earning Capacity Are Supported by Expert Testimony

Dr. Mitchell's life care plan, based on peer-reviewed literature and clinical experience, establishes Plaintiff's future medical needs to a reasonable medical certainty. Similarly, vocational expert Dr. James Brown's analysis demonstrates Plaintiff's complete inability to return to her high-earning technology career.""",
                
                "damages": """Plaintiff respectfully requests compensation for:

1. **Past Medical Expenses**: $347,892 (documented)
2. **Future Medical Expenses**: $1,876,000 (per life care plan)
3. **Past Lost Wages**: $156,000 (18 months at $104,000/year)
4. **Future Lost Earning Capacity**: $2,340,000 (present value)
5. **Pain and Suffering**: Amount to be determined by jury
6. **Loss of Enjoyment of Life**: Amount to be determined by jury

Total Economic Damages: $4,719,892"""
            },
            "citations_formatted": True,
            "word_count": 1847,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def edited_brief() -> Dict[str, Any]:
        """Mock Editor Agent (Gemini 2.5 Pro) response"""
        return {
            "edited_sections": {
                "introduction": """Plaintiff Jane Doe seeks just compensation for catastrophic injuries sustained when Defendant John Smith's reckless decision to run a red light forever altered her life. In a matter of seconds, Ms. Doe—a brilliant software engineer with a promising future—suffered a traumatic brain injury that stripped away her cognitive abilities, her career, and her independence. This case represents not merely a traffic collision, but the destruction of a vibrant life through inexcusable negligence.""",
                
                "improvements_made": [
                    "Enhanced emotional impact in introduction",
                    "Strengthened causal language throughout",
                    "Added specific medical terminology for credibility",
                    "Improved transitions between sections",
                    "Clarified technical concepts for jury comprehension"
                ]
            },
            "style_score": 9.2,
            "clarity_score": 9.5,
            "persuasiveness_score": 9.0,
            "suggested_additions": [
                "Consider adding day-in-the-life examples",
                "Include specific testimony quotes from witnesses",
                "Add comparison to defendant's minor inconvenience vs. plaintiff's lifetime impact"
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_progress_updates() -> List[Dict[str, Any]]:
        """Generate realistic progress updates for frontend"""
        updates = []
        base_time = datetime.now()
        
        stages = [
            ("orchestrator", "Analyzing case documents", 15),
            ("orchestrator", "Identifying legal theories", 25),
            ("legal_research", "Searching legal databases", 35),
            ("legal_research", "Analyzing precedents", 45),
            ("scientific_research", "Reviewing medical literature", 55),
            ("scientific_research", "Consulting expert databases", 65),
            ("brief_writer", "Drafting initial sections", 75),
            ("brief_writer", "Formatting citations", 85),
            ("editor", "Refining language", 92),
            ("editor", "Final review", 100)
        ]
        
        for agent, task, progress in stages:
            updates.append({
                "agent": agent,
                "task": task,
                "progress": progress,
                "timestamp": (base_time + timedelta(seconds=progress * 1.8)).isoformat()
            })
        
        return updates
    
    @staticmethod
    def get_mock_error(error_type: str = "api") -> Dict[str, Any]:
        """Generate mock error for testing error handling"""
        errors = {
            "api": {
                "error": "API rate limit exceeded",
                "code": 429,
                "message": "Too many requests. Please try again in 60 seconds.",
                "agent": "legal_research"
            },
            "parsing": {
                "error": "Document parsing failed",
                "code": 422,
                "message": "Unable to extract text from PDF page 47",
                "agent": "orchestrator"
            },
            "timeout": {
                "error": "Agent timeout",
                "code": 504,
                "message": "Scientific research agent failed to respond within 300 seconds",
                "agent": "scientific_research"
            }
        }
        
        return errors.get(error_type, errors["api"])
    
    @staticmethod
    def get_edge_case_response(case_type: str) -> Dict[str, Any]:
        """Generate edge case responses for testing"""
        edge_cases = {
            "corrupted_wordperfect": {
                "error": "Legacy document format",
                "message": "WordPerfect file detected. Converting to modern format...",
                "converted_text": "PLAINTIFF'S MOTION FOR... [CORRUPTED SECTION] ...hereby moves this honorable court...",
                "confidence": 0.65,
                "warnings": ["Partial data recovery from legacy format", "Manual review recommended"]
            },
            
            "non_english_medical": {
                "detected_language": "Spanish",
                "original_text": "INFORME MÉDICO: Paciente sufrió traumatismo craneoencefálico severo...",
                "translated_text": "MEDICAL REPORT: Patient suffered severe traumatic brain injury...",
                "translation_confidence": 0.92,
                "medical_terms_preserved": ["traumatismo craneoencefálico", "hematoma subdural"]
            },
            
            "conflicting_experts": {
                "conflict_detected": True,
                "expert_1": {
                    "name": "Dr. Smith",
                    "opinion": "Complete recovery unlikely, permanent cognitive deficits",
                    "credentials": "Board certified neurologist, 20 years experience"
                },
                "expert_2": {
                    "name": "Dr. Jones", 
                    "opinion": "Full recovery expected within 12-18 months",
                    "credentials": "Neuropsychologist, defense expert"
                },
                "analysis": "Significant disagreement on prognosis. Recommend focusing on objective imaging and established literature.",
                "suggested_strategy": "Emphasize Dr. Smith's clinical experience and peer-reviewed support"
            },
            
            "massive_pdf": {
                "file_size_mb": 487,
                "page_count": 5234,
                "processing_strategy": "chunked",
                "relevant_sections_found": [
                    {"pages": "122-145", "content": "Expert deposition transcript"},
                    {"pages": "2341-2389", "content": "Medical records"},
                    {"pages": "4122-4156", "content": "Damage calculations"}
                ],
                "processing_time_estimate": "15-20 minutes",
                "memory_usage_mb": 2048
            },
            
            "api_key_rotation": {
                "primary_api_failed": "openai",
                "failover_sequence": ["anthropic", "google"],
                "successfully_completed": True,
                "performance_impact": "20% slower due to failover",
                "recommendations": ["Check OpenAI quota", "Consider load balancing"]
            },
            
            "ambiguous_liability": {
                "liability_assessment": "unclear",
                "factors": {
                    "pro_plaintiff": [
                        "Defendant was speeding (5mph over limit)",
                        "Weather conditions were poor"
                    ],
                    "pro_defendant": [
                        "Plaintiff may have been distracted",
                        "Contributory negligence possible"
                    ]
                },
                "recommended_approach": "Focus on severity of injuries rather than clear liability",
                "alternative_theories": ["Res ipsa loquitur", "Joint and several liability"]
            },
            
            "sealed_records": {
                "sealed_documents_found": 12,
                "categories": ["Juvenile records", "Mental health evaluations", "Settlement agreements"],
                "legal_status": "Motion to unseal required",
                "strategic_value": "High - may contain prior similar incidents",
                "procedural_requirements": "Notice to all parties, in camera review likely"
            },
            
            "statute_limitations_issue": {
                "filing_date": "2023-03-15",
                "incident_date": "2021-03-14",
                "standard_sol": "2 years",
                "status": "Potentially time-barred",
                "exceptions_available": [
                    "Discovery rule - symptoms manifested late",
                    "Defendant concealment",
                    "Minority tolling (if applicable)"
                ],
                "recommended_action": "File immediately with discovery rule affidavit"
            }
        }
        
        return edge_cases.get(case_type, {
            "error": "Unknown edge case",
            "message": f"Edge case '{case_type}' not implemented"
        })
    
    @staticmethod
    def generate_memory_pressure_scenario(size: str = "medium") -> Dict[str, Any]:
        """Generate scenarios for memory pressure testing"""
        scenarios = {
            "small": {
                "documents": 10,
                "avg_size_mb": 5,
                "total_mb": 50,
                "expected_memory_usage_mb": 200,
                "processing_time_seconds": 30
            },
            "medium": {
                "documents": 50,
                "avg_size_mb": 20,
                "total_mb": 1000,
                "expected_memory_usage_mb": 2048,
                "processing_time_seconds": 300
            },
            "large": {
                "documents": 200,
                "avg_size_mb": 50,
                "total_mb": 10000,
                "expected_memory_usage_mb": 8192,
                "processing_time_seconds": 1800,
                "warning": "May require batch processing"
            },
            "extreme": {
                "documents": 1000,
                "avg_size_mb": 100,
                "total_mb": 100000,
                "expected_memory_usage_mb": 16384,
                "processing_time_seconds": 7200,
                "warning": "Requires distributed processing",
                "recommended_approach": "Process in chunks of 50 documents"
            }
        }
        
        return scenarios.get(size, scenarios["medium"])