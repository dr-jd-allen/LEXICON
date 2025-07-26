"""
Example: Using LEXICON to SUPPORT Dr. Kenneth J.D. Allen's Expert Testimony
Demonstrates the pipeline's ability to defend plaintiff's experts
"""

import asyncio
from lexicon_pipeline import LEXICONPipeline
from datetime import datetime
import json

async def support_dr_allen():
    """
    Generate a strong defense of Dr. Allen's methodology and testimony
    This shows LEXICON's capability to support plaintiff's experts
    """
    
    pipeline = LEXICONPipeline()
    
    print("\n" + "="*80)
    print("🛡️ LEXICON: SUPPORTING PLAINTIFF'S EXPERT")
    print("="*80)
    print("Expert: Dr. Kenneth J.D. Allen, Ph.D.")
    print("Strategy: Defend against defendant's Daubert challenge")
    print("Goal: Establish unassailable scientific foundation")
    print("="*80 + "\n")
    
    # Context for the support brief
    case_context = {
        "plaintiff_injuries": "Traumatic brain injury from motor vehicle collision",
        "expert_role": "Plaintiff's neuropsychology expert",
        "defendant_challenge": "Daubert motion claiming unreliable methodology",
        "our_position": "Dr. Allen's methods are gold standard in the field"
    }
    
    print("📋 Case Context:")
    for key, value in case_context.items():
        print(f"   {key}: {value}")
    
    print("\n🚀 Generating defense brief...\n")
    
    try:
        # Generate support brief
        result = await pipeline.process_case(
            target_expert="Dr. Kenneth J.D. Allen",
            case_strategy="support",
            motion_type="Plaintiff's Response to Defendant's Daubert Motion"
        )
        
        # The pipeline will:
        # 1. Search for Dr. Allen's credentials and methodologies
        # 2. Find supporting scientific literature
        # 3. Identify favorable legal precedents
        # 4. Build a strong defense of his methods
        # 5. Anticipate and counter defendant's arguments
        
        # Save the supportive brief
        output_dir = Path("./lexicon-output/support-briefs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        brief_path = output_dir / f"Support_DrAllen_Daubert_Response_{timestamp}.txt"
        
        with open(brief_path, 'w', encoding='utf-8') as f:
            # Add case header
            f.write("IN THE UNITED STATES DISTRICT COURT\n")
            f.write("FOR THE [DISTRICT]\n\n")
            f.write("PLAINTIFF,\n")
            f.write("v.\n")
            f.write("DEFENDANT,\n\n")
            f.write("Case No. [NUMBER]\n\n")
            f.write("PLAINTIFF'S RESPONSE TO DEFENDANT'S\n")
            f.write("DAUBERT MOTION TO EXCLUDE DR. KENNETH J.D. ALLEN\n\n")
            f.write("="*60 + "\n\n")
            f.write(result['final_brief'])
        
        print(f"✅ Support brief saved to: {brief_path}")
        
        # Create summary of supportive findings
        summary = {
            "expert": "Dr. Kenneth J.D. Allen, Ph.D.",
            "strategy": "SUPPORT",
            "key_strengths_identified": [],
            "daubert_factors_satisfied": [],
            "supporting_precedents": [],
            "methodology_validation": []
        }
        
        # Extract key points from the research
        if 'research' in result:
            legal = result['research'].get('legal_research', {})
            scientific = result['research'].get('scientific_research', {})
            
            # The pipeline should have found:
            # - Cases where similar neuropsychological experts were admitted
            # - Scientific validation of TBI assessment methods
            # - Peer acceptance of methodologies
            
            summary['search_strategy'] = "Supporting expert admissibility"
            summary['databases_searched'] = [
                "PubMed (validation studies)",
                "Google Scholar (methodology acceptance)",
                "Legal precedents (successful neuropsych testimony)"
            ]
        
        # Save summary
        summary_path = output_dir / f"Support_Summary_{timestamp}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Summary saved to: {summary_path}")
        
        # Display strategic excerpt
        print("\n" + "="*60)
        print("STRATEGIC SUPPORT EXCERPT:")
        print("="*60)
        print("\n[The brief would establish Dr. Allen's qualifications,")
        print("validate his methodologies, and demonstrate why his")
        print("testimony is both reliable and essential to the case.]")
        print("\nKey Arguments Generated:")
        print("1. Dr. Allen's extensive qualifications in neuropsychology")
        print("2. His methods follow established clinical guidelines")
        print("3. Peer-reviewed support for his diagnostic approach")
        print("4. Favorable precedents admitting similar testimony")
        print("5. Why exclusion would deprive jury of critical evidence")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def demonstrate_versatility():
    """
    Show how LEXICON can switch between supporting and challenging
    """
    print("\n" + "="*80)
    print("🔄 LEXICON'S STRATEGIC VERSATILITY")
    print("="*80)
    print("\nLEXICON is a neutral tool that adapts to your legal strategy:")
    print("\n1. When representing PLAINTIFFS:")
    print("   → SUPPORT your experts (like Dr. Allen)")
    print("   → CHALLENGE defense experts")
    print("\n2. When representing DEFENDANTS:")
    print("   → SUPPORT your experts")
    print("   → CHALLENGE plaintiff's experts")
    print("\n3. Strategic Considerations:")
    print("   → Analyze expert strengths and vulnerabilities")
    print("   → Develop targeted legal arguments")
    print("   → Find supporting or challenging precedents")
    print("   → Generate persuasive briefs for either position")
    print("\nLEXICON is about winning cases, not attacking experts.")
    print("="*80)

if __name__ == "__main__":
    print("🏛️ LEXICON - Balanced Legal Strategy AI")
    print("\nDemonstrating support for plaintiff's expert witness")
    
    # First show versatility
    asyncio.run(demonstrate_versatility())
    
    # Then generate support brief
    input("\nPress Enter to generate support brief for Dr. Allen...")
    asyncio.run(support_dr_allen())