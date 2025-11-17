from pathlib import Path
import json
from typing import Iterator, List

from sentence_transformers import SentenceTransformer

from src.ingest.icon_tokenizer import generate_icon_token_map
from src.ingest.text_icon_merger import merge_icons_into_text
from src.config import EMBEDDING_MODEL


# ---------------------------------------------------------
# STREAMING CHUNK GENERATOR
# ---------------------------------------------------------
def generate_chunks_from_file(
    file_path: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 250,
):
    """
    Stream-safe chunk generator that:
    - never loops infinitely
    - never produces duplicate chunks
    - handles overlap correctly
    - handles last piece safely
    """

    buffer = ""

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            buffer += line

            # While we have enough to produce a chunk
            while len(buffer) >= chunk_size:
                # take the chunk
                chunk = buffer[:chunk_size].rstrip()

                yield chunk

                # safe slice (no infinite loop)
                buffer = buffer[chunk_size - chunk_overlap:]

        # Flush the remainder
        if buffer.strip():
            yield buffer.strip()



# ---------------------------------------------------------
# MICRO-BATCH EMBEDDER (FAST + MEMORY SAFE)
# ---------------------------------------------------------
class MiniLMMicroBatchEmbedder:
    """
    Embeds text in micro-batches for speed and safety.
    No huge memory spikes. Batch size 4 is optimal.
    """

    def __init__(self, model_name: str, batch_size: int = 4):
        self.model = SentenceTransformer(model_name)
        self.batch_size = batch_size

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()


# ---------------------------------------------------------
# FULL PIPELINE
# ---------------------------------------------------------
def build_knowledge_base(
    pdf_path: str,
    classified_icons_path: str,
    out_dir: str,
):
    """
    1. Generate icon token map
    2. Merge tokens with text
    3. Chunk text (streaming)
    4. Embed chunks in micro-batches
    5. Write JSON array incrementally (memory-safe)
    """

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    icon_tokens_path = out_dir / "icon_tokens.json"
    enriched_text_path = out_dir / "text_with_icons.txt"
    rag_output_path = out_dir / "rag_chunks_with_embeddings.json"

    # 1) Icon tokens
    print("Generating icon tokens...")
    generate_icon_token_map(
        classified_path=classified_icons_path,
        output_path=str(icon_tokens_path),
    )

    # 2) Merge icons into text
    print("Merging icons into text...")
    merge_icons_into_text(
        pdf_path=pdf_path,
        tokens_path=str(icon_tokens_path),
        output_path=str(enriched_text_path),
    )

    # 3) Prepare micro-batch embedder
    embedder = MiniLMMicroBatchEmbedder(
        EMBEDDING_MODEL,
        batch_size=4  # best compromise for your machine
    )

    # 4) Stream chunks + embed + write JSON
    print("Embedding chunks (micro-batches)...")

    with rag_output_path.open("w", encoding="utf-8") as f:
        f.write("[\n")
        first = True
        chunk_id = 0

        batch = []

        for chunk in generate_chunks_from_file(str(enriched_text_path)):
            batch.append(chunk)

            # If batch is full → embed
            if len(batch) >= embedder.batch_size:
                vectors = embedder.embed_batch(batch)

                for chunk_text, vector in zip(batch, vectors):
                    record = {
                        "id": f"chunk_{chunk_id}",
                        "text": chunk_text,
                        "embedding": vector,
                        "metadata": {"source": pdf_path},
                    }

                    if not first:
                        f.write(",\n")
                    else:
                        first = False

                    f.write(json.dumps(record))
                    chunk_id += 1

                batch = []

        # Embed remaining small batch
        if batch:
            vectors = embedder.embed_batch(batch)

            for chunk_text, vector in zip(batch, vectors):
                record = {
                    "id": f"chunk_{chunk_id}",
                    "text": chunk_text,
                    "embedding": vector,
                    "metadata": {"source": pdf_path},
                }

                if not first:
                    f.write(",\n")
                else:
                    first = False

                f.write(json.dumps(record))
                chunk_id += 1

        f.write("\n]\n")

    print(f"✓ RAG knowledge base saved: {rag_output_path}")
