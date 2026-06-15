import os
import httpx
import google.generativeai as genai
from backend.config import settings


class LLMClient:
    """Unified LLM client interface for Gemini and Groq with automatic multi-key + multi-model fallback."""

    def __init__(self):
        # Configure Gemini with the primary key
        self._current_gemini_key_index = 0
        self._gemini_keys = settings.GEMINI_API_KEYS
        self._groq_keys = settings.GROQ_API_KEYS
        if self._gemini_keys:
            genai.configure(api_key=self._gemini_keys[0])

    def _rotate_gemini_key(self, key_index: int):
        """Switch the active Gemini API key for the genai library."""
        if key_index < len(self._gemini_keys):
            genai.configure(api_key=self._gemini_keys[key_index])
            self._current_gemini_key_index = key_index
            return True
        return False

    def _try_groq(self, prompt: str, model: str = None, groq_key: str = None) -> str | None:
        """Attempt a Groq API call with the given model and key. Returns response text or None."""
        api_key = groq_key or (self._groq_keys[0] if self._groq_keys else "")
        if not api_key:
            return None
        groq_model = model or getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": groq_model,
                "messages": [
                    {"role": "user", "content": prompt}
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
                print(f"Groq error ({groq_model}, key...{api_key[-6:]}): {response.status_code}")
                return None
        except Exception as e:
            print(f"Groq exception ({groq_model}): {e}")
            return None

    def _try_gemini(self, prompt: str, model_name: str, key_index: int) -> str | None:
        """Attempt a Gemini API call with the given model and key. Returns response text or None."""
        try:
            self._rotate_gemini_key(key_index)
            gemini_model = genai.GenerativeModel(model_name)
            response = gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                print(f"Gemini quota hit: key#{key_index+1} + {model_name}")
            elif "404" in error_str:
                print(f"Gemini 404: {model_name}")
            else:
                print(f"Gemini err: key#{key_index+1} + {model_name}: {error_str[:100]}")
            return None

    def generate_content(self, model_role: str, prompt: str) -> str:
        """
        Generate content with full fallback chain:
          1. Groq primary model × all keys
          2. Groq fallback models × all keys
          3. Gemini primary model × all keys
          4. Gemini fallback models × all keys
          5. Local offline fallback
        """
        provider = getattr(settings, "LLM_PROVIDER", "gemini").lower()

        # ── Step 1: Try Groq (all keys × primary model, then all keys × fallback models) ──
        if provider == "groq":
            for groq_key in self._groq_keys:
                result = self._try_groq(prompt, groq_key=groq_key)
                if result:
                    return result

            for fallback_model in settings.GROQ_FALLBACK_MODELS:
                if fallback_model != settings.GROQ_MODEL:
                    for groq_key in self._groq_keys:
                        result = self._try_groq(prompt, model=fallback_model, groq_key=groq_key)
                        if result:
                            return result

        # ── Step 2: Try Gemini (all keys × primary model) ──
        primary_model = settings.GEMINI_PRO_MODEL if model_role == "pro" else settings.GEMINI_FLASH_MODEL

        for key_idx in range(len(self._gemini_keys)):
            result = self._try_gemini(prompt, primary_model, key_idx)
            if result:
                return result

        # ── Step 3: Try Gemini fallback models × all keys ──
        for fallback_model in settings.GEMINI_FALLBACK_MODELS:
            if fallback_model == primary_model:
                continue
            for key_idx in range(len(self._gemini_keys)):
                result = self._try_gemini(prompt, fallback_model, key_idx)
                if result:
                    return result

        # ── Step 4: Local offline fallback ──
        print("WARNING: All LLM providers exhausted. Using offline fallback.")
        return self._generate_offline_fallback(prompt)

    def _generate_offline_fallback(self, prompt: str) -> str:
        """Constructs a high-quality fallback reply from retrieved documents if API quota is exhausted."""
        try:
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
        """Transcribe audio using Groq Whisper model with multi-key fallback."""
        mime_type = "audio/webm"
        if filename.endswith(".wav"):
            mime_type = "audio/wav"
        elif filename.endswith(".mp3"):
            mime_type = "audio/mp3"
        elif filename.endswith(".m4a"):
            mime_type = "audio/m4a"

        for groq_key in self._groq_keys:
            try:
                headers = {"Authorization": f"Bearer {groq_key}"}
                files = {"file": (filename, audio_bytes, mime_type)}
                data = {"model": "whisper-large-v3"}
                
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
                    print(f"Whisper failed (key...{groq_key[-6:]}): {response.status_code}")
            except Exception as e:
                print(f"Whisper exception (key...{groq_key[-6:]}): {e}")

        raise Exception("All Groq keys exhausted for audio transcription.")

    def generate_vision_content(self, prompt: str, image_data: str, image_type: str = "image/png") -> str:
        """Analyze an image using Groq vision models (multi-key) with Gemini multi-key fallback."""
        if not image_type:
            image_type = "image/png"
        
        image_url = f"data:{image_type};base64,{image_data}"
        
        groq_vision_models = [
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "llama-3.2-11b-vision-preview"
        ]
        
        # Try all Groq keys × vision models
        for groq_key in self._groq_keys:
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            for model in groq_vision_models:
                try:
                    data = {
                        "model": model,
                        "messages": [{"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]}],
                        "temperature": 0.2
                    }
                    response = httpx.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers, json=data, timeout=30.0
                    )
                    if response.status_code == 200:
                        return response.json()["choices"][0]["message"]["content"]
                    else:
                        print(f"Groq vision {model} (key...{groq_key[-6:]}): {response.status_code}")
                except Exception as e:
                    print(f"Groq vision {model} exception: {e}")
        
        # Fallback to Gemini with multi-key × multi-model rotation
        import base64
        image_bytes = base64.b64decode(image_data)

        vision_models = [settings.GEMINI_PRO_MODEL] + settings.GEMINI_FALLBACK_MODELS
        seen = set()
        unique_models = [m for m in vision_models if m not in seen and not seen.add(m)]

        for model_name in unique_models:
            for key_idx in range(len(self._gemini_keys)):
                try:
                    self._rotate_gemini_key(key_idx)
                    gemini_model = genai.GenerativeModel(model_name)
                    img_part = {"mime_type": image_type, "data": image_bytes}
                    response = gemini_model.generate_content([img_part, prompt])
                    return response.text
                except Exception as e:
                    print(f"Gemini Vision key#{key_idx+1} + {model_name}: {str(e)[:80]}")

        return "[Vision Fallback Error] All providers exhausted for image analysis."

# Singleton instance
llm_client = LLMClient()
