# create and save embeddings in FAISS

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load a small, free model (works offline after first download)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def create_vector_store(docs: list[str]):
    """
    Create FAISS index with local sentence-transformer embeddings.
    """
    print("🔹 Creating embeddings locally...")
    vectors = embedding_model.encode(docs, show_progress_bar=True)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(np.array(vectors, dtype="float32"))
    return index, np.array(vectors, dtype="float32")
