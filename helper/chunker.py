# helper/chunker.py

import re
from typing import List
import logging

"""
Chunking utilities for document preprocessing.

This module provides three chunking strategies:
1. Fixed-size with overlap
2. Sentence-based
3. Paragraph-based

These are used to split large documents into manageable pieces
for downstream tasks like embedding and semantic search.
"""
log = logging.getLogger(__name__)


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
    Splits the input text into fixed-size character chunks with overlap.

    Each chunk will contain exactly `size` characters (except the last one),
    and consecutive chunks will overlap by `overlap` characters. This is useful
    for preserving context between chunks.

    Args:
        text (str): The full input text to split.
        size (int, optional): The number of characters per chunk. Defaults to 800.
        overlap (int, optional): The number of overlapping characters between chunks. Defaults to 200.

    Returns:
        List[str]: A list of non-empty, trimmed text chunks.
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
    Splits text into sentence-based chunks, each up to `max_len` characters.

    The text is split by sentence boundaries using punctuation (., !, ?),
    and sentences are grouped into chunks not exceeding the specified maximum length.
    Common abbreviations (e.g., "Dr.", "U.S.") are handled to avoid incorrect splits.

    Args:
        text (str): The full input text to split.
        max_len (int, optional): Maximum number of characters per chunk. Defaults to 1000.

    Returns:
        List[str]: A list of sentence-based text chunks.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string.")
    if max_len <= 0:
        raise ValueError("max_len must be greater than 0.")
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
    Splits text into paragraph-based chunks, each up to `max_len` characters.

    Paragraphs are identified using one or more blank lines, and grouped together
    into chunks without exceeding the maximum allowed length. Suitable for documents
    with well-defined paragraph structure.

    Args:
        text (str): The full input text to split.
        max_len (int, optional): Maximum number of characters per chunk. Defaults to 1200.

    Returns:
        List[str]: A list of paragraph-based text chunks.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string.")
    if max_len <= 0:
        raise ValueError("max_len must be greater than 0.")
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