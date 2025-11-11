from fastapi import APIRouter
from pydantic import BaseModel
from src.qa import ask_question
from helpers.task_classifier import classify_task  # 🧩 New import

router = APIRouter(prefix="/ask", tags=["Ask"])

# Shared state will be injected by main.py
docs = []
index = None
vectors = None

class QuestionRequest(BaseModel):
    question: str

@router.post("/")
def ask_manual_question(req: QuestionRequest):
    """Answer a question using the current manual, with task understanding."""
    global docs, index, vectors

    if not docs or index is None:
        return {"answer": "No manual uploaded yet. Please upload a PDF first."}

    # 🔹 Step 1: Detect task intent
    intent = classify_task(req.question)
    print(f"🧭 Detected intent: {intent}")

    # 🔹 Step 2: Use intent to build smarter prompt and answer
    answer = ask_question(req.question, docs, index, vectors, intent)

    # 🔹 Step 3: Return both intent and answer
    return {"intent": intent, "answer": answer}