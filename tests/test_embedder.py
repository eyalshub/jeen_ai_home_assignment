# tests/test_embedder.py

from helper.embedder import get_embedding
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


@pytest.mark.parametrize("text", [
    "Short.",
    "This is a longer sentence used for testing the robustness of the embedding function.",
    "🚀 Emojis and special characters like ©, ™, ∆ should be handled too.",
])
def test_various_texts(text):
    embedding = get_embedding(text)
    assert isinstance(embedding, list)
    assert len(embedding) == 768


def test_whitespace_only():
    with pytest.raises(ValueError):
        get_embedding("   ")