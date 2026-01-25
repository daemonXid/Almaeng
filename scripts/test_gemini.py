import os
import sys

# Add backend to path to load settings if needed, but let's try standalone first
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))


def test_gemini_connection():
    print("🚀 Testing Gemini API Connection...")

    # 1. Check Env Var
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Try loading from .env manually if not in environment
        try:
            from dotenv import load_dotenv

            load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
            api_key = os.getenv("GEMINI_API_KEY")
        except ImportError:
            print("❌ dotenv module not found. Run 'uv pip install python-dotenv'")
            return

    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment or .env")
        return

    print(f"✅ GEMINI_API_KEY found: {api_key[:5]}...{api_key[-5:]}")

    # 2. Check Library
    try:
        from google import genai

        print("✅ google.genai library imported successfully.")
    except ImportError:
        print("❌ google.genai library NOT found. Run 'uv pip install google-genai'")
        return

    # 3. Test API Call
    try:
        client = genai.Client(api_key=api_key)

        # Try Flash 2.0 first
        model_name = "gemini-2.0-flash-exp"
        print(f"🤖 Testing model: {model_name}...")

        response = client.models.generate_content(
            model=model_name,
            contents="Hello, are you working? Respond with 'Yes, I am Gemini'.",
        )
        print(f"🎉 API Success! Response: {response.text}")

    except Exception as e:
        print(f"❌ API Call Failed with {model_name}: {e}")

        # Fallback to 1.5 Flash
        try:
            model_name = "gemini-1.5-flash"
            print(f"🔄 Retrying with fallback model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents="Hello, are you working? Respond with 'Yes, I am Gemini'.",
            )
            print(f"🎉 API Success with Fallback! Response: {response.text}")
        except Exception as e2:
            print(f"❌ Fallback API Call Failed: {e2}")


if __name__ == "__main__":
    test_gemini_connection()
