# =============================================
#  CONFIGURATION MODULE (Simplified)
#  Loads environment variables and constants
# =============================================

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv()

# --------------------------------------------
# Gemini API configuration
# --------------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("❌ Missing GOOGLE_API_KEY in .env")

genai.configure(api_key=GOOGLE_API_KEY)
print("🚀 Using Gemini API")

# --------------------------------------------
# Model selections
# --------------------------------------------
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# --------------------------------------------
# RAG settings
# --------------------------------------------
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 3))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# --------------------------------------------
# Web scrapping settings
# --------------------------------------------