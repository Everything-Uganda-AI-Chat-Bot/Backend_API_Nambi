import os
import google.generativeai as genai

def get_gemini_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in environment variables")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")
