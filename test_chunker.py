# test_chunker.py

from chunker import chunk_fixed, chunk_by_sentences, chunk_by_paragraphs


sample_text = """
Dr. Smith went to the U.S.A. in 2020. He stayed there until 2023! Can you believe it?

This is a second paragraph. It talks about data science, NLP, and AI.

Another paragraph starts here. It contains abbreviations like etc., i.e., and e.g.

This is a very long paragraph that goes on and on without much punctuation but should still be handled gracefully even if it passes the character limits in the chunking function because the paragraph splitter should still try to keep it together unless it exceeds the max length.
"""


def test_chunk_fixed():
    print("\n🔹 Testing: chunk_fixed")
    chunks = chunk_fixed(sample_text, size=100, overlap=20)
    for i, chunk in enumerate(chunks):
        print(f"[{i+1}] ({len(chunk)} chars): {repr(chunk)}...")


def test_chunk_by_sentences():
    print("\n🔹 Testing: chunk_by_sentences")
    chunks = chunk_by_sentences(sample_text, max_len=150)
    for i, chunk in enumerate(chunks):
        print(f"[{i+1}] ({len(chunk)} chars): {repr(chunk)}...")


def test_chunk_by_paragraphs():
    print("\n🔹 Testing: chunk_by_paragraphs")
    chunks = chunk_by_paragraphs(sample_text, max_len=200)
    for i, chunk in enumerate(chunks):
        print(f"[{i+1}] ({len(chunk)} chars): {repr(chunk)}...")


if __name__ == "__main__":
    test_chunk_fixed()
    test_chunk_by_sentences()
    test_chunk_by_paragraphs()
