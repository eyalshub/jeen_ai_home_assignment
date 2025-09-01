# chunker.py

import re
from typing import List

COMMON_ABBREVIATIONS = {
    "Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "Sr.", "Jr.",
    "St.", "Mt.", "Capt.", "Sgt.", "Col.", "Gen.",
    "Inc.", "Ltd.", "Co.", "Corp.",
    "e.g.", "i.e.", "etc.", "vs.",
    "U.S.", "U.S.A.", "U.K.", "EU.", "UN.",
    "Jan.", "Feb.", "Mar.", "Apr.", "Aug.", "Sept.", "Oct.", "Nov.", "Dec.",
}
def chunk_fixed(text: str, size: int = 800, overlap: int = 200) -> List[str]:
    """
    Splits text into fixed-size chunks with overlap.
    Example: size=800, overlap=200 will give sliding windows of 800 chars, 
    with 200 chars overlapping between consecutive chunks.
    """
    tokens = list(text)
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i+size]
        chunks.append("".join(chunk).strip())
        i += size - overlap
    return [c for c in chunks if c]


def chunk_by_sentences(text: str, max_len: int = 1000) -> List[str]:
    """
    Splits text based on sentence boundaries.
    Groups sentences into chunks not exceeding max_len characters.
    """
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    buffer = ""

    for sentence in raw_sentences:
        last_word = buffer.strip().split()[-1] if buffer.strip() else ""
        if last_word in COMMON_ABBREVIATIONS:
            buffer += " " + sentence
        elif len(buffer) + len(sentence) < max_len:
            buffer += " " + sentence if buffer else sentence
        else:
            if buffer:
                chunks.append(buffer.strip())
            buffer = sentence

    if buffer:
        chunks.append(buffer.strip())

    return [c for c in chunks if c]


def chunk_by_paragraphs(text: str, max_len: int = 1200) -> List[str]:
    """
    Splits text based on paragraphs (blank lines or double newlines).
    Groups paragraphs into chunks not exceeding max_len characters.
    """
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()

    paragraphs = re.split(r"\n\s*\n", text)
    chunks = []
    buffer = ""

    for para in paragraphs:
        if len(buffer) + len(para) < max_len:
            buffer += "\n\n" + para
        else:
            chunks.append(buffer.strip())
            buffer = para
    if buffer:
        chunks.append(buffer.strip())

    return [c for c in chunks if c]
