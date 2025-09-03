# tests/test_chunker.py

import pytest
from helper.chunker import chunk_fixed, chunk_by_sentences, chunk_by_paragraphs

sample_text = """
Dr. Smith went to the U.S.A. in 2020. He stayed there until 2023! Can you believe it?

This is a second paragraph. It talks about data science, NLP, and AI.

Another paragraph starts here. It contains abbreviations like etc., i.e., and e.g.

This is a very long paragraph that goes on and on without much punctuation but should still be handled gracefully even if it passes the character limits in the chunking function because the paragraph splitter should still try to keep it together unless it exceeds the max length.
"""

def test_chunk_fixed_basic():
    chunks = chunk_fixed(sample_text, size=100, overlap=20)
    assert all(len(chunk) <= 100 for chunk in chunks)
    assert len(chunks) > 1
    assert isinstance(chunks[0], str)

def test_chunk_by_sentences_basic():
    chunks = chunk_by_sentences(sample_text, max_len=150)
    assert isinstance(chunks, list)
    assert len(chunks) > 1
    assert all(isinstance(c, str) and len(c) > 0 for c in chunks)
    assert any("U.S.A." in c for c in chunks)

def test_chunk_by_paragraphs_basic():
    chunks = chunk_by_paragraphs(sample_text, max_len=200)
    assert isinstance(chunks, list)
    assert len(chunks) > 1
    assert all(isinstance(c, str) and len(c) > 0 for c in chunks)
    assert any("data science" in c for c in chunks)

@pytest.mark.parametrize("text", ["", "short sentence."])
def test_chunk_edge_cases(text):
    assert isinstance(chunk_fixed(text, size=50, overlap=10), list)
    assert isinstance(chunk_by_sentences(text, max_len=50), list)
    assert isinstance(chunk_by_paragraphs(text, max_len=50), list)
