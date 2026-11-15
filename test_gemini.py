from google import genai
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.getenv("GEMINI_API_KEY")
print("API Key:", api_key[:10] + "..." if api_key else "None")

if api_key:
    client = genai.Client(api_key=api_key)
    try:
        print("Listing models:")
        for m in client.models.list():
            print(f" - {m.name}")
    except Exception as e:
        print("Error listing models:", str(e))
else:
    print("No GEMINI_API_KEY found in .env")

