import os
from dotenv import load_dotenv
from fireworks.client import Fireworks

# Load environment variables
load_dotenv()

def test_fireworks_connection():
    """Test connection to Fireworks AI API"""
    try:
        # Get API key from environment
        api_key = os.getenv("FIREWORKS_API_KEY")
        model_name = os.getenv("FIREWORKS_MODEL")
        
        if not api_key:
            print("❌ ERROR: FIREWORKS_API_KEY not found in .env file")
            return False
        
        print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
        print(f"🤖 Model: {model_name}")
        
        # Initialize Fireworks client
        client = Fireworks(api_key=api_key)
        
        # Test API call
        print("🚀 Testing Fireworks AI connection...")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hello, are you working? Respond briefly."}],
            max_tokens=50,
            temperature=0.7
        )
        
        # Print response
        if response and response.choices:
            print("✅ SUCCESS: Fireworks AI is working!")
            print(f"💬 Response: {response.choices[0].message.content}")
            return True
        else:
            print("❌ ERROR: No response from Fireworks AI")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔥 Fireworks AI Connection Test")
    print("=" * 40)
    
    success = test_fireworks_connection()
    
    print("=" * 40)
    if success:
        print("🎉 All tests passed! Your Fireworks AI is ready.")
    else:
        print("💥 Some tests failed. Check your API key and configuration.")