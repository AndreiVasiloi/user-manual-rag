import google.generativeai as genai
from src.config import GEMINI_MODEL

def classify_task(question: str) -> str:
    """
    Classify the user's question into a general intent category.
    Works across different types of manuals (electronics, appliances, etc.).
    """
    prompt = f"""
    You are an intent classifier for a question-answering system about product manuals.
    Classify the question into ONE of the following categories:
    - instruction (how to use or operate something)
    - setup (installation, configuration, connection)
    - diagnosis (problem solving, errors, troubleshooting)
    - maintenance (cleaning, replacing, servicing, schedule)
    - explanation (meaning or purpose of something)
    - safety (warnings, dangers, prohibited actions)

    Question: "{question}"

    Respond with only one category name.
    """

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        intent = response.text.strip().lower()

        allowed = ["instruction", "setup", "diagnosis", "maintenance", "explanation", "safety"]
        return intent if intent in allowed else "explanation"

    except Exception as e:
        print(f"⚠️ Intent classification failed: {e}")
        return "explanation"
