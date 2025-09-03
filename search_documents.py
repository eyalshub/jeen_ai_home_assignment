# search_documents.py
import logging
from typing import List, Dict, Callable, Optional, Any, Tuple
from helper.database import pooled_connection
from helper.embedder import get_embedding, l2_normalize

log = logging.getLogger(__name__)


def embed_text_gemini(text: str) -> List[float]:
    """
    Embeds a free-text query using Gemini and normalizes the vector.

    Args:
        text (str): Input query.

    Returns:
        List[float]: Normalized embedding vector.
    """
    return l2_normalize(get_embedding(text))


def build_where_clause(
    filename: Optional[str],
    strategy: Optional[str],
) -> Tuple[str, List[Any]]:
    """
    Build WHERE SQL clause based on optional filters.

    Args:
        filename (str, optional): Filter by document name.
        strategy (str, optional): Filter by chunking strategy.

    Returns:
        Tuple[str, List[Any]]: SQL WHERE clause and parameters.
    """

    clauses = []
    values = []

    if filename:
        clauses.append("filename = %s")
        values.append(filename)

    if strategy:
        clauses.append("split_strategy = %s")
        values.append(strategy)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where_sql, values

def search_documents(
    query_text: str,
    top_k: int = 5,
    *,
    embed_fn: Callable[[str], List[float]] = embed_text_gemini,
    filename: Optional[str] = None,
    strategy: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Perform semantic search over the 'chunks' table using cosine similarity.

    Args:
        query_text (str): Free-text query to embed and compare.
        top_k (int): Number of top results to return.
        embed_fn (Callable): Function to embed the query.
        filename (str, optional): Filter by source filename.
        strategy (str, optional): Filter by chunking strategy.

    Returns:
        List[Dict[str, Any]]: Top matching chunks and scores.
    """


    if not query_text.strip():
        log.warning("Received empty query text. Skipping search.")

        return []
    
    try:
        # 1. Embed query
        log.info("Embedding query text...")
        q_vec = embed_fn(query_text)
        dim = len(q_vec)

        # 2. Prepare WHERE clause
        where_sql, where_params = build_where_clause(filename, strategy)

        # 3. SQL query (string only, no f-strings inside values!)
        sql = """
        WITH q AS (
            SELECT %s::vector(%s) AS e
        )
        SELECT
            id, chunk_text, filename, split_strategy, created_at,
            (1.0 - (embedding <=> q.e)) AS cosine_sim
        FROM chunks, q
        {where_clause}
        ORDER BY embedding <=> q.e
        LIMIT %s;
        """.format(where_clause=where_sql)

        params = [q_vec, dim] + where_params + [top_k]

        # 4. Execute query
        log.info("Running semantic search query...")
        results = []
        with pooled_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
                for r in rows:
                    _id, text, fname, strat, created, sim = r
                    results.append({
                        "id": _id or "N/A",
                        "chunk_text": text or "",
                        "filename": fname or "unknown",
                        "split_strategy": strat or "unspecified",
                        "created_at": created.isoformat() if created else None,
                        "score": float(sim) if sim is not None else 0.0
                    })
        log.info(f"✅ Search completed. Found {len(results)} results.")
        return results

    except Exception as e:
        log.exception(f"❌ Error during semantic search: {e}")
        return []

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Semantic Search CLI")
    parser.add_argument("query", type=str, help="Free-text query")
    parser.add_argument("--filename", type=str, help="Filter by filename", default=None)
    parser.add_argument("--strategy", type=str, choices=["fixed", "sentence", "paragraph"], default=None)
    parser.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args()

    results = search_documents(
        query_text=args.query,
        top_k=args.top_k,
        filename=args.filename,
        strategy=args.strategy
    )

    for i, r in enumerate(results, 1):
        print(f"\n[{i}] Score: {r['score']:.4f} | File: {r['filename']}, Strategy: {r['split_strategy']}")
        print(r["chunk_text"][:300] + ("..." if len(r["chunk_text"]) > 300 else ""))
