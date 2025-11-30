import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ No API Key found.")
else:
    print(f"✅ Key found: {api_key[:5]}...")
    try:
        genai.configure(api_key=api_key)
        print("\n--- YOUR AVAILABLE MODELS ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        print("-----------------------------")
    except Exception as e:
        print(f"❌ Error listing models: {e}")