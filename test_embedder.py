# test_embedder.py

from embedder import get_embedding
import pytest

def test_embedding_length():
    text = "Artificial Intelligence is transforming education."
    embedding = get_embedding(text)

    assert isinstance(embedding, list), "❌ Output is not a list"
    assert all(isinstance(x, float) for x in embedding), "❌ Not all elements are floats"
    assert len(embedding) == 768, f"❌ Expected embedding of length 768, got {len(embedding)}"

    print(f"✅ Got embedding with {len(embedding)} dimensions")
    print("🔹 First 5 dimensions:", embedding[:5])


def test_empty_string():
    with pytest.raises(ValueError):
        get_embedding("")

