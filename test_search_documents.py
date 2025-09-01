# test_search_documents.py

import pytest
import numpy as np
from search_documents import search_documents
from database import get_connection, insert_chunk


# ---------- Fixtures ----------

@pytest.fixture(autouse=True)
def clear_chunks():
    """Clean the 'chunks' table before each test."""
    print("\n🧼 Clearing table before test...")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM chunks;")
            conn.commit()


@pytest.fixture
def seeded_chunks():
    """
    Seeds known embeddings into the database to test semantic search.
    Uses deterministic vectors to avoid test flakiness.
    """
    print("🌱 Seeding deterministic chunks...")

    def make_vec(val: float):
        # Builds a normalized vector [val, 0, 0, ..., 0] → cosine similarity will match val
        vec = np.array([val] + [0.0]*767)
        return vec / np.linalg.norm(vec)

    for sim in [0.99, 0.95, 0.75, 0.5, 0.2]:
        insert_chunk(
            chunk_text=f"Chunk with sim {sim}",
            embedding=make_vec(sim),
            filename="test.docx",
            strategy="fixed"
        )

    # Unrelated chunk with lower similarity
    insert_chunk(
        chunk_text="Other file chunk",
        embedding=make_vec(0.3),
        filename="other.docx",
        strategy="dynamic"
    )


@pytest.fixture
def fake_embed_fn():
    """
    Returns a static embedding vector similar to base_vec
    to simulate a realistic cosine search scenario.
    """
    def _fn(text: str):
        vec = np.array([1.0] + [0.0]*767)
        return vec / np.linalg.norm(vec)
    return _fn

# ---------- Helper ----------

def print_results(results):
    print(f"\n📦 {len(results)} results returned:")
    for i, r in enumerate(results, start=1):
        print(f"\n--- Result #{i} ---")
        print(f"📝 Text       : {r['chunk_text'][:60]}...")
        print(f"📁 Filename   : {r['filename']}")
        print(f"🔀 Strategy   : {r['split_strategy']}")
        print(f"📊 Score      : {r['score']:.4f}")
        print(f"📅 Created at : {r['created_at']}")


# ---------- Tests ----------

def test_returns_sorted_by_score(seeded_chunks, fake_embed_fn):
    print("🔍 Test: results are sorted by score")
    results = search_documents("test query", embed_fn=fake_embed_fn)
    print_results(results)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_respects_top_k(seeded_chunks, fake_embed_fn):
    print("🔍 Test: respects top_k")
    results = search_documents("test query", top_k=3, embed_fn=fake_embed_fn)
    print_results(results)
    assert len(results) == 3


def test_filters_by_filename(seeded_chunks, fake_embed_fn):
    print("🔍 Test: filters by filename")

    all_results = search_documents("test query", embed_fn=fake_embed_fn, top_k=6)
    filtered_results = search_documents("test query", embed_fn=fake_embed_fn, filename="test.docx")

    filenames_all = {r['filename'] for r in all_results}
    filenames_filtered = {r['filename'] for r in filtered_results}

    print("All filenames:", filenames_all)
    print("Filtered filenames:", filenames_filtered)

    assert "other.docx" in filenames_all
    assert filenames_filtered == {"test.docx"}


def test_filters_by_strategy(seeded_chunks, fake_embed_fn):
    print("🔍 Test: filters by strategy")
    filtered = search_documents("test query", embed_fn=fake_embed_fn, strategy="fixed")
    strategies = {r["split_strategy"] for r in filtered}
    print("Returned strategies:", strategies)
    assert strategies == {"fixed"}


def test_score_threshold_for_similar_vectors(seeded_chunks, fake_embed_fn):
    print("🔍 Test: score should be high for close vectors")
    results = search_documents("test query", top_k=1, embed_fn=fake_embed_fn)
    top_score = results[0]["score"]
    print_results(results)
    assert top_score > 0.8


def test_returns_empty_on_blank_query(fake_embed_fn):
    print("🔍 Test: empty query returns empty list")
    results = search_documents("", embed_fn=fake_embed_fn)
    assert results == []


def test_returns_empty_when_no_matches(clear_chunks, fake_embed_fn):
    print("🔍 Test: no results when table is empty")
    results = search_documents("test query", embed_fn=fake_embed_fn)
    assert results == []


def test_top_result_has_expected_text(seeded_chunks, fake_embed_fn):
    print("🔍 Test: top result has expected text")
    results = search_documents("test query", embed_fn=fake_embed_fn)
    print_results(results)

    top_text = results[0]["chunk_text"]
    expected_prefixes = [
        "Chunk with sim 0.99",
        "Chunk with sim 0.95",
        "Chunk with sim 0.75"
    ]
    assert any(top_text.startswith(p) for p in expected_prefixes)


def test_scores_do_not_exceed_1(seeded_chunks, fake_embed_fn):
    print("🔍 Test: scores should be ≤ 1.0")
    results = search_documents("test query", embed_fn=fake_embed_fn)
    for r in results:
        assert r["score"] <= 1.0


def test_low_score_for_unrelated_query(seeded_chunks):
    print("🔍 Test: unrelated query returns low score")
    def unrelated_embed(text: str):
        vec = np.array([0.0] * 768)
        vec[-1] = 1.0  # completely unrelated direction
        return vec

    results = search_documents("something totally unrelated", embed_fn=unrelated_embed)
    print_results(results)
    assert results[0]["score"] < 0.3  # Should be low similarity
