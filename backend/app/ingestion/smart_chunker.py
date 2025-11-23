import re
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP


def split_by_headings(text: str):
    """
    Split markdown text by headings (#, ##, ###).
    Keeps the heading with the content.
    Returns list of (section_title, section_text).
    """
    blocks = []
    current_title = "General"
    current_text = []

    lines = text.split("\n")

    for line in lines:
        if re.match(r"^#{1,6}\s", line):
            # Save previous block
            if current_text:
                blocks.append((current_title, "\n".join(current_text)))
                current_text = []

            current_title = line.lstrip("#").strip()
        else:
            current_text.append(line)

    # last block
    if current_text:
        blocks.append((current_title, "\n".join(current_text)))

    return blocks


def chunk_text(text: str, max_len=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Sliding-window chunking while preserving meaning.
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + max_len, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += max_len - overlap

    return chunks


def chunk_markdown_smart(text: str):
    """
    Hybrid chunker: split by headings → then sliding window inside each section.
    """
    sections = split_by_headings(text)
    final_chunks = []

    for section_title, section_text in sections:
        small_chunks = chunk_text(section_text)

        for ch in small_chunks:
            final_chunks.append({
                "section": section_title,
                "content": ch
            })

    return final_chunks
