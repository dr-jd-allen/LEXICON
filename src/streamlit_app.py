#!/usr/bin/env python3
"""
Streamlit interface for LEXICON MVP
Simple web interface for Daubert motion generation
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
from docx_generator import DaubertMotionGenerator
from dify_workflow import DifyWorkflow
from typing import Dict

# Page config
st.set_page_config(
    page_title="LEXICON - Daubert Motion Generator",
    page_icon="⚖️",
    layout="wide"
)

# Initialize components
@st.cache_resource
def init_components():
    return {
        'workflow': DifyWorkflow(),
        'generator': DaubertMotionGenerator()
    }

def main():
    st.title("⚖️ LEXICON - Daubert Motion Generator")
    st.markdown("### AI-Powered Expert Witness Challenge System")
    st.markdown("*Powered by Spinwheel AI*")
    
    # Initialize components
    components = init_components()
    
    # Sidebar for case information
    with st.sidebar:
        st.header("Case Information")
        
        case_info = {
            'district': st.text_input("District", "NORTHERN DISTRICT OF CALIFORNIA"),
            'plaintiff': st.text_input("Plaintiff Name", "John Doe"),
            'defendant': st.text_input("Defendant Name", "ABC Corporation"),
            'case_number': st.text_input("Case Number", "3:24-cv-12345"),
            'expert_name': st.text_input("Expert Name", "Dr. Jane Smith"),
            'attorney_name': st.text_input("Attorney Name", "Your Name"),
            'bar_number': st.text_input("Bar Number", "123456"),
            'law_firm': st.text_input("Law Firm", "Your Law Firm"),
            'address': st.text_input("Address", "123 Main St, Suite 100"),
            'phone': st.text_input("Phone", "(555) 123-4567"),
            'email': st.text_input("Email", "attorney@lawfirm.com")
        }
        
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Generate Daubert Motion")
        
        # Expert name input
        expert_name = st.text_input(
            "Enter Expert Witness Name",
            value=case_info['expert_name'],
            help="This should match the name as it appears in the case documents"
        )
        
        # Knowledge base status
        st.subheader("Knowledge Base Status")
        kb_status = st.container()
        with kb_status:
            st.info("📚 Case File Knowledge Base: Ready")
            st.info("⚖️ Precedent Knowledge Base: Ready")
            
            # LEXIS-NEXIS integration toggle
            use_lexis = st.checkbox(
                "🔍 Use LEXIS-NEXIS for Enhanced Precedent Research",
                value=True,
                help="Searches federal and state cases for relevant Daubert challenges"
            )
            
            if use_lexis:
                st.success("✅ LEXIS-NEXIS Integration: Active")
        
        # Generate button
        if st.button("🚀 Generate Motion", type="primary", use_container_width=True):
            with st.spinner("Analyzing expert testimony and generating motion..."):
                try:
                    # Update case info with expert name
                    case_info['expert_name'] = expert_name
                    
                    # Progress tracking
                    progress = st.progress(0)
                    status = st.empty()
                    
                    # Step 1: Extract opinions
                    status.text("📋 Extracting expert opinions...")
                    progress.progress(25)
                    
                    # Step 2: Find contradictions
                    status.text("🔍 Finding contradictions in testimony...")
                    progress.progress(50)
                    
                    # Step 3: Research precedent
                    status.text("📚 Researching legal precedent...")
                    progress.progress(75)
                    
                    # Step 4: Draft motion
                    status.text("✍️ Drafting motion arguments...")
                    
                    # Execute workflow (mock for demo)
                    # In production, this would call: components['workflow'].execute_workflow(expert_name)
                    argument_text = generate_mock_argument(expert_name)
                    
                    progress.progress(90)
                    
                    # Generate document
                    status.text("📄 Generating Word document...")
                    output_path = components['generator'].generate_motion(
                        argument_text=argument_text,
                        case_info=case_info
                    )
                    
                    progress.progress(100)
                    status.success("✅ Motion generated successfully!")
                    
                    # Store in session state
                    st.session_state['last_motion'] = {
                        'path': str(output_path),
                        'argument': argument_text,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                except Exception as e:
                    st.error(f"❌ Error generating motion: {str(e)}")
        
        # Display results
        if 'last_motion' in st.session_state:
            st.header("Generated Motion")
            
            # Download button
            with open(st.session_state['last_motion']['path'], 'rb') as file:
                st.download_button(
                    label="📥 Download Motion (.docx)",
                    data=file.read(),
                    file_name=Path(st.session_state['last_motion']['path']).name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            
            # Preview argument section
            with st.expander("Preview Argument Section"):
                st.markdown(st.session_state['last_motion']['argument'])
    
    with col2:
        st.header("Recent Generations")
        
        # Mock history for demo
        history = [
            {"expert": "Dr. Jane Smith", "date": "2025-01-15", "status": "✅"},
            {"expert": "Dr. Robert Jones", "date": "2025-01-14", "status": "✅"},
            {"expert": "Dr. Emily Brown", "date": "2025-01-13", "status": "✅"}
        ]
        
        for item in history:
            st.info(f"{item['status']} {item['expert']} - {item['date']}")

def generate_mock_argument(expert_name: str) -> str:
    """Generate mock argument for demo purposes."""
    return f"""
I. INTRODUCTION

Defendant respectfully moves to exclude the testimony of {expert_name} because their opinions lack scientific reliability and are based on methodologies that fail to meet the standards set forth in Daubert. The expert's conclusions regarding traumatic brain injury causation are speculative, unsupported by peer-reviewed literature, and contradicted by the medical evidence in this case.

II. THE EXPERT'S UNRELIABLE METHODOLOGY

A. Diffusion Tensor Imaging (DTI) Analysis Lacks Scientific Validity

{expert_name}'s primary methodology relies on DTI analysis, which multiple courts have found unreliable for individual TBI diagnosis. In Henderson v. State Farm, 2023 WL 123456 (N.D. Cal. 2023), the court excluded similar DTI-based testimony, finding that "DTI remains an experimental technique unsuitable for courtroom use in individual cases."

The expert's DTI analysis suffers from several fatal flaws:
- No established error rates for individual diagnosis
- Lack of standardized protocols across imaging centers
- Failure to account for normal anatomical variations
- No peer-reviewed validation studies for forensic use

B. Failure to Rule Out Alternative Causes

{expert_name} failed to conduct a proper differential diagnosis. The expert did not adequately consider or rule out pre-existing conditions, medication effects, or psychological factors that could explain the plaintiff's symptoms.

III. CONTRADICTIONS WITH CASE FACTS

The expert's opinions directly contradict the contemporaneous medical records:

1. Emergency room records show the plaintiff was alert and oriented immediately post-accident, with a Glasgow Coma Scale of 15/15.

2. Initial CT scans were negative for any acute intracranial abnormality.

3. The plaintiff returned to work within 48 hours and worked full-time for three months before claiming disability.

4. During deposition, {expert_name} admitted to not reviewing the plaintiff's prior medical history, which includes treatment for migraines and anxiety disorders.

IV. LEGAL PRECEDENT MANDATES EXCLUSION

Courts consistently exclude TBI expert testimony that relies on speculative methodologies:

- Meyers v. Illinois Central R.R., 629 F.3d 639 (7th Cir. 2010): Excluded expert testimony based on DTI where the methodology was not generally accepted.

- Chapman v. Procter & Gamble, 766 F.3d 1296 (11th Cir. 2014): Affirmed exclusion of expert who failed to rule out alternative causes.

- Davis v. City of Detroit, 2022 WL 789012 (E.D. Mich. 2022): Excluded TBI expert who relied on subjective symptom reporting without objective findings.

V. CONCLUSION

{expert_name}'s testimony fails every Daubert factor: the methodology cannot be tested, has not been peer-reviewed for forensic use, has unknown error rates, lacks accepted standards, and is not generally accepted in the relevant scientific community. The Court should exclude this unreliable testimony to prevent jury confusion and prejudice.
"""

if __name__ == "__main__":
    main()