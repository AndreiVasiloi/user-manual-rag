import google.generativeai as genai
from app.core.config import GOOGLE_API_KEY, GEMINI_MODEL

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)


def generate_answer(question: str, retrieved_chunks):
    """
    Builds a prompt that includes:
    - retrieved chunks (some include <icon:...> tokens)
    - icon meanings detected in chunk text
    """

    context_texts = [c["text"] for c in retrieved_chunks]

    prompt = f"""
You are a helpful assistant answering based ONLY on the user manual below.

The manual includes icon tokens like <icon:ground_coffee_button>.
These tokens represent user-interface symbols. If the question is about an icon, explain its meaning.

Question:
{question}

Relevant manual sections:
{chr(10).join(context_texts)}

Answer clearly and ONLY using the manual content.
"""

    response = model.generate_content(prompt)
    return response.text
