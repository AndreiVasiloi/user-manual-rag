from fastapi import APIRouter
from pydantic import BaseModel
from src.qa import ask_question

router = APIRouter(prefix="/ask", tags=["Ask"])

# Shared state will be injected by main.py
docs = []
index = None
vectors = None

class QuestionRequest(BaseModel):
    question: str

@router.post("/")
def ask_manual_question(req: QuestionRequest):
    """Answer a question using the current manual."""
    global docs, index, vectors

    if not docs or index is None:
        return {"answer": "No manual uploaded yet. Please upload a PDF first."}

    answer = ask_question(req.question, docs, index, vectors)
    return {"answer": answer}
