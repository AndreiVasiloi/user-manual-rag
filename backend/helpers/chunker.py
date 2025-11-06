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