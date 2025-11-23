import json
from pathlib import Path
from app.ingestion.smart_chunker import chunk_markdown_smart
from app.rag.vector_store import LocalVectorStore
from sentence_transformers import SentenceTransformer
from app.core.config import EMBEDDING_MODEL


def ingest_markdown(md_path: str, out_dir: str):
    """
    Ingest a markdown file and create chunks + embeddings.
    Produces rag_chunks_with_embeddings.json inside out_dir.
    """
    md_path = Path(md_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    text = md_path.read_text(encoding="utf-8")

    # 1. Smart chunking
    chunks = chunk_markdown_smart(text)

    # 2. Embeddings
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode([c["content"] for c in chunks]).tolist()

    # 3. Combine chunks + embeddings
    rag_data = []
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        rag_data.append({
            "id": idx,
            "text": chunk["content"],
            "section": chunk["section"],
            "embedding": emb
        })

    out_file = out_dir / "rag_chunks_with_embeddings.json"
    out_file.write_text(json.dumps(rag_data, indent=2), encoding="utf-8")

    return str(out_file)
