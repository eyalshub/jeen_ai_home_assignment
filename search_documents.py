from typing import List, Dict, Callable, Optional, Any, Tuple
from database import get_connection
from embedder import get_embedding, l2_normalize


def embed_text_gemini(text: str) -> List[float]:
    return l2_normalize(get_embedding(text))


def build_where_clause(
    filename: Optional[str],
    strategy: Optional[str],
) -> Tuple[str, List[Any]]:
    """
    Builds the WHERE condition based on optional parameters.
     Returns the SQL snippet and the corresponding parameters.
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
    Performs semantic search:
    - Converts query to embedding
    - Compares against embeddings in chunks table
    - Returns the five most similar by cosine similarity
    """


    if not query_text.strip():
        return []
    
    # 1. Embed the query
    q_vec = embed_fn(query_text)

  
    # 2. WHERE conditions (optional)
    where_sql, where_params = build_where_clause(filename, strategy)

    # 3. SQL query using pgvector cosine distance
    sql = f"""
    WITH q AS (
        SELECT %s::vector({len(q_vec)}) AS e
    )
    SELECT
        id, chunk_text, filename, split_strategy, created_at,
        (1.0 - (embedding <=> q.e)) AS cosine_sim
    FROM chunks, q
    {where_sql}
    ORDER BY embedding <=> q.e
    LIMIT %s;
    """

    params = [q_vec] + where_params + [top_k]

    # 4. Execute and return results
    results = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            for r in rows:
                _id, text, fname, strat, created, sim = r
                results.append({
                    "id": _id,
                    "chunk_text": text,
                    "filename": fname,
                    "split_strategy": strat,
                    "created_at": created,
                    "score": float(sim)
                })
    return results