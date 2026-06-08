import os
import httpx
import google.generativeai as genai
from backend.config import settings

class LLMClient:
    """Unified LLM client interface for Gemini and Groq with automatic fallback."""

    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
    def generate_content(self, model_role: str, prompt: str) -> str:
        """
        Generate content using the active provider (Gemini or Groq).
        model_role: 'flash' or 'pro' (determines the model tier)
        """
        provider = getattr(settings, "LLM_PROVIDER", "gemini").lower()
        groq_api_key = getattr(settings, "GROQ_API_KEY", "")

        if provider == "groq" and groq_api_key:
            groq_model = getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
            try:
                headers = {
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": groq_model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                }
                # Synchronous request using httpx (which is installed with FastAPI)
                response = httpx.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    print(f"Groq API error {response.status_code}: {response.text}. Falling back to Gemini.")
            except Exception as e:
                print(f"Groq API exception: {e}. Falling back to Gemini.")

        # Default/Fallback to Gemini
        # Map role to configured Gemini models
        if model_role == "pro":
            gemini_model_name = settings.GEMINI_PRO_MODEL
        else:
            gemini_model_name = settings.GEMINI_FLASH_MODEL
            
        try:
            gemini_model = genai.GenerativeModel(gemini_model_name)
            response = gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API generation error: {e}")
            raise e

# Singleton instance
llm_client = LLMClient()
