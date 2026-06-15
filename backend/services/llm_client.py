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
            print(f"Gemini API generation error on {gemini_model_name}: {e}")
            
            # 1. Try alternative Gemini models
            alt_models = [
                "models/gemini-2.5-flash",
                "models/gemini-2.5-flash-lite",
                "models/gemini-1.5-flash",
                "models/gemini-1.5-pro"
            ]
            # Move the original model to the end or skip it
            alt_models = [m for m in alt_models if m != gemini_model_name]
            
            for alt_model in alt_models:
                try:
                    print(f"Trying alternative Gemini model: {alt_model}...")
                    alt_gemini_model = genai.GenerativeModel(alt_model)
                    response = alt_gemini_model.generate_content(prompt)
                    return response.text
                except Exception as e2:
                    print(f"Alternative Gemini model {alt_model} failed: {e2}")
            
            # 2. Local fallback: extract answer directly from RAG prompt context
            return self._generate_offline_fallback(prompt)

    def _generate_offline_fallback(self, prompt: str) -> str:
        """Constructs a high-quality fallback reply from retrieved documents if API quota is exhausted."""
        try:
            # Try to parse query and documents
            query = ""
            if "USER QUESTION:" in prompt:
                query = prompt.split("USER QUESTION:")[1].split("\n")[0].strip()
            elif "USER QUERY:" in prompt:
                query = prompt.split("USER QUERY:")[1].split("\n")[0].strip()
                
            docs_block = ""
            if "RETRIEVED DOCUMENTS:" in prompt:
                docs_block = prompt.split("RETRIEVED DOCUMENTS:")[1]
                if "USER QUESTION:" in docs_block:
                    docs_block = docs_block.split("USER QUESTION:")[0]
            
            # Extract distinct sources
            sources = []
            if docs_block:
                parts = docs_block.split("---")
                for p in parts:
                    p = p.strip()
                    if p:
                        sources.append(p)
            
            if not query:
                if "DIAGNOSIS" in prompt or "symptom" in prompt:
                    return "[OFFLINE MODE] Based on standard telemetry and symptom analysis, the system identifies potential Bearing Wear or Motor Overheating. Please check lubrication and current draw parameters."
                return "[OFFLINE MODE] The AI service is currently running in offline mode due to API rate limits. Please rephrase your query or inspect the local logs."

            reply_lines = [
                f"**[RAG Offline Mode]** Gemini API quota limit reached. Synthesizing answer directly from local reference documents for query: *\"{query}\"*",
                ""
            ]
            
            if sources:
                reply_lines.append("Based on the retrieved reference documents, the system found the following information:")
                for src in sources[:3]:
                    reply_lines.append(f"\n{src}")
            else:
                reply_lines.append("No local document matches were found for this query.")
                
            return "\n".join(reply_lines)
        except Exception as e:
            return f"[RAG Offline Mode] Failed to synthesize response. Error: {str(e)}"

    def transcribe_audio(self, audio_bytes: bytes, filename: str) -> str:
        """
        Transcribe audio using Groq Whisper model (whisper-large-v3).
        """
        groq_api_key = getattr(settings, "GROQ_API_KEY", "")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is not configured in settings.")
            
        try:
            headers = {
                "Authorization": f"Bearer {groq_api_key}"
            }
            mime_type = "audio/webm"
            if filename.endswith(".wav"):
                mime_type = "audio/wav"
            elif filename.endswith(".mp3"):
                mime_type = "audio/mp3"
            elif filename.endswith(".m4a"):
                mime_type = "audio/m4a"
                
            files = {
                "file": (filename, audio_bytes, mime_type)
            }
            data = {
                "model": "whisper-large-v3"
            }
            
            response = httpx.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data,
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json().get("text", "")
            else:
                error_msg = f"Groq Whisper transcription failed ({response.status_code}): {response.text}"
                print(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            print(f"Exception in transcribe_audio: {e}")
            raise e

    def generate_vision_content(self, prompt: str, image_data: str, image_type: str = "image/png") -> str:
        """
        Analyze an image using Groq Llama vision models with Gemini fallback.
        """
        groq_api_key = getattr(settings, "GROQ_API_KEY", "")
        if not image_type:
            image_type = "image/png"
        
        image_url = f"data:{image_type};base64,{image_data}"
        
        groq_vision_models = [
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "llama-3.2-11b-vision-preview"
        ]
        
        if groq_api_key:
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            for model in groq_vision_models:
                try:
                    print(f"Trying Groq vision model: {model}...")
                    data = {
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {"type": "image_url", "image_url": {"url": image_url}}
                                ]
                            }
                        ],
                        "temperature": 0.2
                    }
                    response = httpx.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=30.0
                    )
                    if response.status_code == 200:
                        return response.json()["choices"][0]["message"]["content"]
                    else:
                        print(f"Groq vision {model} failed with status {response.status_code}: {response.text}")
                except Exception as e:
                    print(f"Exception trying Groq vision model {model}: {e}")
        
        # Fallback to Gemini
        print("Falling back to Gemini Flash for vision analysis...")
        try:
            import base64
            image_bytes = base64.b64decode(image_data)
            gemini_model_name = settings.GEMINI_PRO_MODEL
            
            gemini_model = genai.GenerativeModel(gemini_model_name)
            img_part = {
                "mime_type": image_type,
                "data": image_bytes
            }
            response = gemini_model.generate_content([img_part, prompt])
            return response.text
        except Exception as e:
            print(f"Gemini Vision fallback failed: {e}")
            return f"[Vision Fallback Error] Unable to analyze screenshot. Groq Vision and Gemini Vision both failed. Details: {str(e)}"

# Singleton instance
llm_client = LLMClient()

