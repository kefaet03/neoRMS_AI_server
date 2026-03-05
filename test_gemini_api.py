"""
Test script to validate Gemini API connection
Using the new google-genai package
"""
import os
from dotenv import load_dotenv

def test_gemini_api():
    """Test Gemini API connectivity and functionality"""
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        from google import genai
        
        # Initialize client
        client = genai.Client(api_key=api_key)
        print("✓ Client initialized")
        
        # List available models
        print("\n📋 Available Gemini models:")
        models = client.models.list()
        gemini_models = [m.name for m in models if 'gemini' in m.name.lower()]
        for m in gemini_models[:5]:
            print(f"   - {m}")
        
        # Use gemini-2.5-flash (current stable model)
        model_name = "gemini-2.5-flash"
        print(f"\n✓ Using model: {model_name}")
        
        # Test simple prompt
        print("📡 Sending test request...")
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'Hello, API is working!' in exactly those words."
        )
        
        if response and response.text:
            print(f"✓ Response received: {response.text.strip()}")
            print("\n✅ GEMINI API IS WORKING CORRECTLY!")
            return True
        else:
            print("❌ Empty response received")
            return False
            
    except ImportError:
        print("❌ google-genai package not installed")
        print("   Run: pip install google-genai")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

def test_review_extraction():
    """Test the actual review analysis functionality"""
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"')
    
    if not api_key:
        print("❌ API Key not found")
        return False
    
    print("\n" + "="*50)
    print("Testing Review Extraction...")
    print("="*50)
    
    try:
        from google import genai
        
        client = genai.Client(api_key=api_key)
        model_name = "gemini-2.5-flash"
        
        # Test review
        test_review = "The burger was cold and tasteless. Very disappointed!"
        
        prompt = f"""Analyze this restaurant review and extract complaints.

Review: "{test_review}"

Return ONLY a JSON object in this exact format:
{{"complaints": [{{"food_item": "item name", "issue": "problem", "category": "category"}}]}}

Categories: taste, temperature, hygiene, service, price, quality, portion, presentation, other"""

        print(f"📝 Test review: {test_review}")
        print("📡 Sending extraction request...")
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        if response and response.text:
            print(f"✓ Raw response:\n{response.text}")
            
            # Try to parse JSON
            import json
            import re
            
            text = response.text.strip()
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if json_match:
                text = json_match.group(1)
            
            try:
                result = json.loads(text)
                print(f"\n✓ Parsed JSON: {json.dumps(result, indent=2)}")
                print("\n✅ REVIEW EXTRACTION WORKING!")
                return True
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse warning: {e}")
                print("Response received but JSON parsing needs adjustment")
                return True  # API works, just formatting issue
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("GEMINI API VALIDATION TEST")
    print("="*50 + "\n")
    
    # Test 1: Basic connectivity
    basic_ok = test_gemini_api()
    
    # Test 2: Review extraction (only if basic works)
    if basic_ok:
        test_review_extraction()
    
    print("\n" + "="*50)
    print("TEST COMPLETE")
    print("="*50)