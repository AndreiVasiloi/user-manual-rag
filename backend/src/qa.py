import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from src.config import *
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from src.config import GEMINI_MODEL, GOOGLE_API_KEY

embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# 🧩 Define intent-specific styles
INTENT_TEMPLATES = {
    "instruction": "Answer with clear, numbered steps.",
    "setup": "Explain how to install or configure it properly.",
    "diagnosis": "List possible causes and recommended solutions.",
    "maintenance": "Explain how and when to perform maintenance.",
    "safety": "List all relevant safety warnings and precautions.",
    "explanation": "Provide a clear and concise explanation.",
}

def build_prompt(context: str, question: str, intent: str) -> str:
    """Generate a dynamic prompt based on the user's intent."""
    template = """
    You are a helpful assistant that answers questions strictly based on the provided product manual.

    Manual context:
    {context}

    Question:
    {question}

    {style}
    """
    return PromptTemplate(
        input_variables=["context", "question", "style"],
        template=template.strip(),
    )


def ask_question(
    question: str,
    docs: list[str],
    index,
    vectors,
    intent: str = "explanation",
    top_k: int = 3,
):
    """
    Retrieve top-k relevant chunks and ask Gemini (via LangChain) for an answer.
    Uses local embeddings for retrieval, and LangChain for LLM call.
    """

    # 1️⃣ Compute embeddings for the question
    q_vector = embedding_model.encode([question])
    distances, indices = index.search(np.array(q_vector, dtype="float32"), top_k)

    # 2️⃣ Get relevant chunks
    retrieved_chunks = [docs[i] for i in indices[0]]
    context = "\n\n".join(retrieved_chunks)

    # 3️⃣ Build the intent-aware prompt
    style = INTENT_TEMPLATES.get(intent, "Answer clearly and concisely.")

    prompt = build_prompt(context, question, intent)

    # 4️⃣ Initialize Gemini model via LangChain
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,
    )

    # 5️⃣ Chain prompt → model
    chain = prompt | llm
    response = chain.invoke(
        {"context": context, "question": question, "style": style}
    )

    return response.content.strip()