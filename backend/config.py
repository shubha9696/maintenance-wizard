"""Configuration management for the Maintenance Wizard backend services."""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_KEY_2: str = os.getenv("GEMINI_API_KEY_2", "")
    GEMINI_API_KEY_3: str = os.getenv("GEMINI_API_KEY_3", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_KEY_2: str = os.getenv("GROQ_API_KEY_2", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_FALLBACK_MODEL: str = os.getenv("GROQ_FALLBACK_MODEL", "llama-3.1-8b-instant")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    GEMINI_FLASH_MODEL: str = "models/gemini-2.5-flash-lite"
    GEMINI_PRO_MODEL: str = "models/gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/gemini-embedding-2"
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data", "generated")
    KNOWLEDGE_DIR: str = os.path.join(os.path.dirname(__file__), "data", "equipment_knowledge")

    @property
    def GEMINI_API_KEYS(self) -> list:
        """Returns all available Gemini API keys for rotation fallback."""
        keys = []
        for k in [self.GEMINI_API_KEY, self.GEMINI_API_KEY_2, self.GEMINI_API_KEY_3]:
            if k:
                keys.append(k)
        return keys

    @property
    def GROQ_API_KEYS(self) -> list:
        """Returns all available Groq API keys for rotation fallback."""
        keys = []
        for k in [self.GROQ_API_KEY, self.GROQ_API_KEY_2]:
            if k:
                keys.append(k)
        return keys

    # Ordered list of Gemini models to try (newest/freshest quota first)
    GEMINI_FALLBACK_MODELS: list = [
        "models/gemini-3.5-flash",
        "models/gemini-3.1-flash-lite",
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.5-flash",
        "models/gemini-2.5-flash-lite",
    ]

    # Ordered list of Groq models to try
    GROQ_FALLBACK_MODELS: list = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "qwen/qwen3-32b",
    ]

settings = Settings()
