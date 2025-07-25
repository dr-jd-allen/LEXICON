"""
Test LEXICON Pipeline with both challenge and support strategies
"""
import asyncio
from lexicon_pipeline import LEXICONPipeline
from pathlib import Path
import json

async def test_both_strategies():
    """
    Test the pipeline with both challenge AND support strategies
    Shows LEXICON's versatility in legal strategy
    """
    pipeline = LEXICONPipeline()
    
    # Let's test with YOUR expert profile, Dr. Allen
    test_expert = "Kenneth J.D. Allen"
    
    print("\n" + "="*80)
    print("🧪 LEXICON PIPELINE TEST - DUAL STRATEGY DEMONSTRATION")
    print("="*80)
    print(f"Testing with: Dr. {test_expert}")
    print("Demonstrating both SUPPORT and CHALLENGE capabilities")
    print("="*80 + "\n")
    
    # Test 1: SUPPORT our expert (plaintiff's expert)
    print("\n📋 TEST 1: SUPPORTING OUR EXPERT (Plaintiff's Expert)")
    print("-" * 60)
    
    try:
        support_result = await pipeline.process_case(
            target_expert=test_expert,
            case_strategy="support",
            motion_type="Response to Defendant's Daubert Motion"
        )
        
        # Save support brief
        output_dir = Path("./lexicon-output/test-briefs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        support_path = output_dir / f"SUPPORT_{test_expert.replace(' ', '_')}_response.txt"
        with open(support_path, 'w', encoding='utf-8') as f:
            f.write(support_result['final_brief'])
        
        print(f"✅ Support brief saved to: {support_path}")
        
    except Exception as e:
        print(f"❌ Error in support test: {e}")
    
    # Test 2: CHALLENGE opposing expert (defense's expert)
    print("\n\n📋 TEST 2: CHALLENGING OPPOSING EXPERT (Defense's Expert)")
    print("-" * 60)
    
    # For demo, we'll use a hypothetical opposing expert
    opposing_expert = "Dr. Steven Rothke"  # From your corpus
    
    try:
        challenge_result = await pipeline.process_case(
            target_expert=opposing_expert,
            case_strategy="challenge",
            motion_type="Motion in Limine to Exclude Defense Expert"
        )
        
        challenge_path = output_dir / f"CHALLENGE_{opposing_expert.replace(' ', '_').replace('.', '')}_motion.txt"
        with open(challenge_path, 'w', encoding='utf-8') as f:
            f.write(challenge_result['final_brief'])
        
        print(f"✅ Challenge brief saved to: {challenge_path}")
        
    except Exception as e:
        print(f"❌ Error in challenge test: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"1. SUPPORT brief for Dr. {test_expert} - Response to Daubert")
    print(f"2. CHALLENGE brief for {opposing_expert} - Motion to Exclude")
    print("\nLEXICON demonstrates neutral, strategy-driven capabilities")
    print("="*80)

async def interactive_test():
    """
    Interactive test allowing user to choose expert and strategy
    """
    pipeline = LEXICONPipeline()
    
    print("\n" + "="*80)
    print("🎯 LEXICON PIPELINE - INTERACTIVE TEST")
    print("="*80)
    
    # Common experts from the corpus
    experts = [
        "Kenneth J.D. Allen",
        "Dr. Steven Rothke",
        "Guy William Fried",
        "Lauren A. Richerson"
    ]
    
    print("\nAvailable experts from corpus:")
    for i, expert in enumerate(experts, 1):
        print(f"  {i}. {expert}")
    print(f"  {len(experts) + 1}. Enter custom expert name")
    
    choice = input("\nSelect expert (1-5): ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(experts):
        target_expert = experts[int(choice) - 1]
    else:
        target_expert = input("Enter expert name: ")
    
    print("\nSelect strategy:")
    print("  1. SUPPORT (defend this expert)")
    print("  2. CHALLENGE (exclude this expert)")
    
    strategy_choice = input("\nSelect strategy (1-2): ")
    case_strategy = "support" if strategy_choice == "1" else "challenge"
    
    print("\nSelect motion type:")
    if case_strategy == "support":
        print("  1. Response to Daubert Motion")
        print("  2. Response to Motion in Limine")
        print("  3. Affirmative Motion to Qualify Expert")
    else:
        print("  1. Daubert Motion to Exclude")
        print("  2. Motion in Limine")
        print("  3. Motion to Strike Expert Testimony")
    
    motion_choice = input("\nSelect motion type (1-3): ")
    
    if case_strategy == "support":
        motion_types = [
            "Response to Defendant's Daubert Motion",
            "Response to Motion in Limine",
            "Motion to Qualify Expert Witness"
        ]
    else:
        motion_types = [
            "Daubert Motion to Exclude Expert Testimony",
            "Motion in Limine to Exclude Expert",
            "Motion to Strike Expert Testimony"
        ]
    
    motion_type = motion_types[int(motion_choice) - 1] if motion_choice.isdigit() and 1 <= int(motion_choice) <= 3 else motion_types[0]
    
    print(f"\n🚀 Generating {case_strategy.upper()} brief for {target_expert}...")
    print(f"📄 Motion type: {motion_type}")
    
    try:
        result = await pipeline.process_case(
            target_expert=target_expert,
            case_strategy=case_strategy,
            motion_type=motion_type
        )
        
        # Save the brief
        output_dir = Path("./lexicon-output/interactive-briefs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{case_strategy.upper()}_{target_expert.replace(' ', '_').replace('.', '')}_{timestamp}.txt"
        brief_path = output_dir / filename
        
        with open(brief_path, 'w', encoding='utf-8') as f:
            f.write(result['final_brief'])
        
        print(f"\n✅ Brief saved to: {brief_path}")
        print(f"📄 Length: {len(result['final_brief'])} characters")
        
        # Show excerpt
        print("\n" + "="*60)
        print("BRIEF EXCERPT:")
        print("="*60)
        print(result['final_brief'][:800] + "...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    Main menu for testing
    """
    print("\n" + "="*80)
    print("🏛️ LEXICON LEGAL AI PIPELINE TEST SUITE")
    print("="*80)
    print("\nThis system can both SUPPORT and CHALLENGE expert witnesses")
    print("Demonstrating neutral, strategy-driven legal AI")
    print("\nSelect test mode:")
    print("  1. Run dual strategy demonstration")
    print("  2. Interactive test (choose expert and strategy)")
    print("  3. Exit")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == "1":
        asyncio.run(test_both_strategies())
    elif choice == "2":
        asyncio.run(interactive_test())
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()