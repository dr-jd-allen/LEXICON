"""
Test LEXICON API Configuration
Verifies all API keys are properly configured
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

print("LEXICON API Configuration Test")
print("=" * 60)

# Test API key presence
apis = {
    'Anthropic (Claude)': os.getenv('ANTHROPIC_API_KEY'),
    'OpenAI (GPT)': os.getenv('OPENAI_API_KEY'),
    'Google AI (Gemini)': os.getenv('GOOGLEAI_STUDIO_API_KEY'),
    'SerpAPI (Scholar)': os.getenv('SERP_API_KEY')
}

print("\nAPI Key Status:")
print("-" * 40)
all_configured = True
for name, key in apis.items():
    if key:
        print(f"[OK] {name}: Configured ({key[:20]}...)")
    else:
        print(f"[MISSING] {name}: Not configured")
        all_configured = False

# Test Gemini specifically
print("\n\nTesting Gemini 2.5 Pro Configuration:")
print("-" * 40)
try:
    genai.configure(api_key=os.getenv('GOOGLEAI_STUDIO_API_KEY'))
    
    # List available models
    print("Available Gemini models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
    
    # Try to initialize Gemini 2.5 Pro
    print("\nAttempting to initialize Gemini 2.5 Pro...")
    try:
        model = genai.GenerativeModel('gemini-2.0-pro-exp')
        print("[OK] Gemini 2.5 Pro (experimental) initialized successfully!")
    except Exception as e:
        print(f"[FAILED] Failed to initialize gemini-2.0-pro-exp: {e}")
        print("\nTrying alternative model names...")
        
        # Try other possible model names
        alternatives = ['gemini-pro', 'gemini-1.5-pro', 'gemini-pro-latest']
        for alt in alternatives:
            try:
                model = genai.GenerativeModel(alt)
                print(f"[OK] {alt} initialized successfully!")
                break
            except:
                print(f"[FAILED] {alt} not available")
                
except Exception as e:
    print(f"[ERROR] Gemini configuration failed: {e}")

# Summary
print("\n\nSummary:")
print("=" * 60)
if all_configured:
    print("[SUCCESS] All API keys are configured!")
    print("\nNext steps:")
    print("1. Run the full pipeline test: python test_lexicon_pipeline.py")
    print("2. Access the web interface: http://localhost:5000")
    print("3. Test external research: python test_agent3_scientific_search.py")
else:
    print("[WARNING] Some API keys are missing. Please check your .env file.")

print("\n\nNote: Gemini 2.5 Pro may be in experimental/preview status.")
print("The exact model name might be:")
print("  - gemini-2.0-pro-exp")
print("  - gemini-exp-1206") 
print("  - gemini-pro-latest")
print("Check https://ai.google.dev/models for current model names.")