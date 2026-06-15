"""Configuration management for the Maintenance Wizard backend."""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    GEMINI_FLASH_MODEL: str = "models/gemini-2.5-flash-lite"
    GEMINI_PRO_MODEL: str = "models/gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/gemini-embedding-2"
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data", "generated")
    KNOWLEDGE_DIR: str = os.path.join(os.path.dirname(__file__), "data", "equipment_knowledge")

settings = Settings()
