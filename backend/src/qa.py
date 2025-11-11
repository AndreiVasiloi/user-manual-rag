import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from src.config import *
import openai


embedding_model = SentenceTransformer(EMBEDDING_MODEL)
openai.api_key = os.getenv("OPENAI_API_KEY")

def build_prompt(context: str, question: str, intent: str) -> str:
    """Generate a dynamic prompt based on the user's intent."""
    base = (
        "You are a helpful assistant that answers questions based only on the provided product manual.\n\n"
        f"Manual context:\n{context}\n\n"
        f"Question: {question}\n\n"
    )

    templates = {
        "instruction": "Answer with clear, numbered steps.",
        "setup": "Explain how to install or configure it properly.",
        "diagnosis": "List possible causes and recommended solutions.",
        "maintenance": "Explain how and when to perform maintenance.",
        "safety": "List all relevant safety warnings and precautions.",
        "explanation": "Provide a clear and concise explanation.",
    }

    return base + templates.get(intent, "Answer clearly and concisely.")

def ask_question(question: str, docs: list[str], index, vectors, intent: str = "explanation", top_k: int = 3):
    """
    Retrieve top-k relevant chunks and ask Gemini for an answer.
    Includes task understanding via the 'intent' parameter.
    """
    q_vector = embedding_model.encode([question])
    distances, indices = index.search(np.array(q_vector, dtype="float32"), top_k)
    retrieved_chunks = [docs[i] for i in indices[0]]
    context = "\n\n".join(retrieved_chunks)
    prompt = build_prompt(context, question, intent)

    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()
