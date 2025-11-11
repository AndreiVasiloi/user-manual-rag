# Load OpenAI key from .env

# =============================================
#  CONFIGURATION MODULE
#  Loads all environment variables and constants
# =============================================

import os
from dotenv import load_dotenv
import google.generativeai as genai

# === Load environment variables ===
load_dotenv()

# === Explicit provider selection ===
# You manually set this in .env → ACTIVE_PROVIDER=gemini OR openai
ACTIVE_PROVIDER = os.getenv("ACTIVE_PROVIDER", "gemini").lower()

# === API keys ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ===  Configure provider ===
if ACTIVE_PROVIDER == "gemini":
    if not GOOGLE_API_KEY:
        raise ValueError("❌ GOOGLE_API_KEY missing but ACTIVE_PROVIDER='gemini'.")
    genai.configure(api_key=GOOGLE_API_KEY)
    print("🚀 Using Gemini model provider.")
elif ACTIVE_PROVIDER == "openai":
    if not OPENAI_API_KEY:
        raise ValueError("❌ OPENAI_API_KEY missing but ACTIVE_PROVIDER='openai'.")
    print("🚀 Using OpenAI model provider.")
else:
    raise ValueError(f"❌ Unknown ACTIVE_PROVIDER: '{ACTIVE_PROVIDER}'")

# === Model names ===
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# === Embedding configuration ===
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# === RAG / FAISS settings ===
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 3))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# === Data paths ===
DATA_DIR = os.getenv("DATA_DIR", "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
MANUALS_DIR = os.path.join(DATA_DIR, "manuals")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MANUALS_DIR, exist_ok=True)




