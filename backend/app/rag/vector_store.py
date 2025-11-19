import json
import numpy as np
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm

from app.core.config import EMBEDDING_MODEL

class LocalVectorStore:
    def __init__(self, rag_json_path: str):
        # Load chunks + embeddings
        with open(rag_json_path, "r", encoding="utf-8") as f:
            self.records = json.load(f)

        self.embeddings = np.array([r["embedding"] for r in self.records])
        self.texts = [r["text"] for r in self.records]
        self.ids = [r["id"] for r in self.records]

        self.embedder = SentenceTransformer(EMBEDDING_MODEL)

    def embed_query(self, query: str):
        return self.embedder.encode([query])[0]

    def search(self, query: str, top_k: int = 5):
        q = self.embed_query(query)
        sims = (self.embeddings @ q) / (norm(self.embeddings, axis=1) * norm(q))
        idx = np.argsort(-sims)[:top_k]

        return [
            {
                "id": self.ids[i],
                "score": float(sims[i]),
                "text": self.texts[i]
            }
            for i in idx
        ]