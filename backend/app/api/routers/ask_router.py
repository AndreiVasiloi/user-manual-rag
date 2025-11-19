from fastapi import APIRouter
from pydantic import BaseModel

from app.qa.task_classifier import classify_task
from app.qa.answer_engine import generate_answer
from app.rag.vector_store import LocalVectorStore

router = APIRouter(prefix="/ask", tags=["Ask"])

# Loaded in main.py → initialized once at startup
vector_store: LocalVectorStore | None = None


class QuestionRequest(BaseModel):
    question: str


@router.post("/")
def ask_manual_question(req: QuestionRequest):
    """Answer a question using the icon-enriched RAG manual."""
    global vector_store

    if vector_store is None:
        return {"answer": "No manual uploaded yet. Please upload a PDF first."}

    # 1. Detect task intent
    intent = classify_task(req.question)
    print(f"🧭 Detected intent: {intent}")

    # 2. Retrieve top chunks with icons embedded
    results = vector_store.search(req.question, top_k=5)

    # 3. Generate final LLM answer (icon-aware)
    answer = generate_answer(req.question, results)

    return {
        "intent": intent,
        "answer": answer,
        "chunks": results  # optional but useful for debugging
    }
