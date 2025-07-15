import streamlit as st
import os
from datetime import datetime
# from src.document_processor import DocumentProcessor
# from src.lexis_nexis_integration import LexisNexisResearcher
import tempfile
import json

# Health check endpoint for Cloud Run
if st.query_params.get("health") == "check":
    st.write("OK")
    st.stop()

# Page config
st.set_page_config(
    page_title="LEXICON - Legal AI Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'results' not in st.session_state:
    st.session_state.results = {}

# Header
st.title("⚖️ LEXICON: Legal Expertise with Contextual Intelligence")
st.markdown("### Generate Daubert/Frye motions and other legal documents with AI")

# Sidebar for inputs
with st.sidebar:
    st.header("Case Information")
    
    brief_type = st.selectbox(
        "Motion Type",
        ["Daubert/Frye motion", "Other motions in limine", "Opposition to MIL"]
    )
    
    expert_name = st.text_input("Expert Name", placeholder="Dr. John Smith")
    
    jurisdiction = st.multiselect(
        "Jurisdiction",
        ["Indiana", "Illinois", "Federal"],
        default=["Federal"]
    )
    
    case_id = st.text_input("Case ID", placeholder="2024-CV-12345")
    
    # File upload
    st.header("Case Files")
    uploaded_files = st.file_uploader(
        "Upload case files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True
    )
    
    # LEXIS-NEXIS credentials (optional)
    with st.expander("LEXIS-NEXIS Access (Optional)"):
        lexis_user = st.text_input("Username", value="Brown, Robert4")
        lexis_pass = st.text_input("Password", type="password", value="baileYI")

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.header("Analysis Pipeline")
    
    # Process button
    if st.button("🚀 Generate Motion", type="primary", disabled=not (expert_name and uploaded_files)):
        with st.spinner("Processing documents..."):
            # Save uploaded files temporarily
            temp_dir = tempfile.mkdtemp()
            file_paths = []
            
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)
            
            # Process documents (mock for now)
            # processor = DocumentProcessor(input_dir=temp_dir, output_dir=temp_dir + "/processed")
            # processor.process_batch(file_paths)
            
        # Show progress for each stage
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Stage 1: Research Agent
        status_text.text("🔍 Analyzing expert testimony...")
        progress_bar.progress(25)
        
        # Mock analysis for demo (replace with actual API calls)
        research_summary = f"""
        ## Expert Analysis: {expert_name}
        
        ### 🚨 CRITICAL FLAGS SUMMARY
        - Methodology lacks peer-reviewed validation
        - Missing error rates for key tests
        - Temporal inconsistency in testing timeline
        
        ### Qualifications Review
        - Board certification expired 2019
        - 80% of income from litigation
        - Testified 47 times in last 3 years (45 for plaintiffs)
        """
        
        # Stage 2: Find Contradictions
        status_text.text("🔎 Finding contradictions...")
        progress_bar.progress(50)
        
        contradictions = """
        ### Key Contradictions Found:
        1. **Report vs. Deposition**: Changed opinion on causation
        2. **Timeline Issue**: Testing performed 18 months post-injury
        3. **Missing Data**: Failed to review prior medical records
        """
        
        # Stage 3: Legal Research
        status_text.text("📚 Researching legal precedent...")
        progress_bar.progress(75)
        
        precedent = f"""
        ### Supporting Precedent ({', '.join(jurisdiction)}):
        - *Daubert v. Merrell Dow*, 509 U.S. 579 (1993)
        - *Kumho Tire Co. v. Carmichael*, 526 U.S. 137 (1999)
        - State-specific cases for methodology challenges
        """
        
        # Stage 4: Draft Motion
        status_text.text("📝 Drafting motion...")
        progress_bar.progress(100)
        
        # Store results
        st.session_state.results = {
            'research': research_summary,
            'contradictions': contradictions,
            'precedent': precedent,
            'brief_type': brief_type,
            'expert_name': expert_name,
            'jurisdiction': jurisdiction
        }
        st.session_state.analysis_complete = True
        status_text.text("✅ Analysis complete!")

# Results display
if st.session_state.analysis_complete:
    with col2:
        st.header("Analysis Results")
        
        tabs = st.tabs(["📊 Summary", "🔍 Contradictions", "📚 Precedent", "📄 Draft Motion"])
        
        with tabs[0]:
            st.markdown(st.session_state.results['research'])
        
        with tabs[1]:
            st.markdown(st.session_state.results['contradictions'])
        
        with tabs[2]:
            st.markdown(st.session_state.results['precedent'])
        
        with tabs[3]:
            motion_text = f"""
            # MOTION TO EXCLUDE EXPERT TESTIMONY OF {st.session_state.results['expert_name'].upper()}
            
            ## I. INTRODUCTION
            
            Defendant respectfully moves this Court to exclude the testimony of 
            {st.session_state.results['expert_name']} pursuant to Federal Rule of 
            Evidence 702 and *Daubert v. Merrell Dow Pharmaceuticals, Inc.*, 
            509 U.S. 579 (1993).
            
            ## II. ARGUMENT
            
            ### A. The Expert's Methodology Lacks Scientific Reliability
            
            [Full motion text would be generated here based on the analysis]
            
            ## III. CONCLUSION
            
            For the foregoing reasons, Defendant respectfully requests that this 
            Court exclude the testimony of {st.session_state.results['expert_name']}.
            
            Respectfully submitted,
            [Your firm name]
            """
            
            st.markdown(motion_text)
            
            # Download button
            st.download_button(
                label="📥 Download Motion (Word)",
                data=motion_text,
                file_name=f"Motion_to_Exclude_{st.session_state.results['expert_name'].replace(' ', '_')}.md",
                mime="text/markdown"
            )

# Footer
st.markdown("---")
st.caption("LEXICON v1.6 - Powered by OpenAI, Anthropic, and Google AI")