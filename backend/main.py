from fastapi.params import File
from pydantic import BaseModel
from src.loader import extract_text_from_pdf
from src.vector_store import create_vector_store
from src.qa import ask_question
from pathlib import Path
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil

app = FastAPI()

# ✅ Allow requests from Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global cache of current manual
docs = []
index = None
vectors = None

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ✅ Request body schema
class QuestionRequest(BaseModel):
    question: str

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks for better retrieval.
    - chunk_size: number of characters per chunk
    - overlap: how many characters to overlap between chunks
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]

        # Avoid cutting words mid-way
        if end < text_length:
            last_period = chunk.rfind(".")
            if last_period != -1 and last_period > chunk_size * 0.6:
                chunk = chunk[:last_period + 1]

        chunks.append(chunk.strip())
        start += chunk_size - overlap

    # 🔍 Debugging section
    filtered = [c for c in chunks if len(c) > 100]
    print(f"📄 Chunking summary:")
    print(f"   - Total raw chunks: {len(chunks)}")
    print(f"   - Kept after filtering (>100 chars): {len(filtered)}")
    print(f"   - Average length of kept chunks: {sum(len(c) for c in filtered) // max(1, len(filtered))}")
    print(f"   - Example chunk preview:\n     {filtered[0][:200]}...\n" if filtered else "     (No valid chunks found)\n")

    return filtered

# ✅ Load the manual once (at startup)
manual_path = Path("data/manuals/user_manual.pdf")
text = extract_text_from_pdf(manual_path)
# docs = [chunk.strip() for chunk in text.split("\n\n") if len(chunk.strip()) > 100]
docs = chunk_text(text, chunk_size=1000, overlap=200)
index, vectors = create_vector_store(docs)


@app.post("/upload")
async def upload_manual(file: UploadFile = File(...)):
    """Upload a new user manual (PDF)."""
    global docs, index, vectors

    # Save uploaded PDF to disk
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text and rebuild vector store
    text = extract_text_from_pdf(file_path)
    chunks = [chunk.strip() for chunk in text.split("\n\n") if len(chunk.strip()) > 100]
    index, vectors = create_vector_store(chunks)
    docs = chunks

    print(f"✅ Uploaded and indexed: {file.filename} ({len(chunks)} chunks)")
    return {"message": f"File '{file.filename}' uploaded and processed successfully."}


@app.post("/ask")
def ask_manual_question(req: QuestionRequest):
    """Answer a question using the current manual."""
    if not docs or index is None:
        return {"answer": "No manual uploaded yet. Please upload a PDF first."}

    answer = ask_question(req.question, docs, index, vectors)
    return {"answer": answer}


# if __name__ == "__main__":
#     manual_path = Path("backend/data/manuals/user_manual.pdf")
#     text = extract_text_from_pdf(manual_path)

#     # Use improved chunking logic
#     docs = chunk_text(text, chunk_size=1000, overlap=200)

#     index, vectors = create_vector_store(docs)

#     print(f"✅ Manual loaded and indexed ({len(docs)} chunks). You can now ask questions.\n")
#     while True:
#         question = input("❓ Your question (or 'exit'): ")
#         if question.lower() == "exit":
#             break
#         answer = ask_question(question, docs, index, vectors)
#         print(f"\n💬 {answer}\n")
