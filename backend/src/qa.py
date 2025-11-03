import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from src.config import *

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Use a lightweight Gemini model (you can change to gemini-1.5-pro if you have access)
MODEL_NAME = "gemini-2.0-flash"

def ask_question(question: str, docs: list[str], index, vectors, top_k: int = 3):
    """
    Retrieve top-k most relevant chunks using FAISS and ask Gemini for an answer.
    """
    q_vector = embedding_model.encode([question])
    distances, indices = index.search(np.array(q_vector, dtype="float32"), top_k)
    retrieved_chunks = [docs[i] for i in indices[0]]
    context = "\n\n".join(retrieved_chunks)

    prompt = (
        "You are a helpful assistant that answers questions based only on the provided manual.\n\n"
        f"Manual context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer clearly and concisely."
    )

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text.strip()
