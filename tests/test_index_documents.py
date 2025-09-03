# tests/test_index_documents.py

import os
import uuid
import ast
import pytest
import psycopg2
from pathlib import Path
from index_documents import process_file
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = int(os.getenv("POSTGRES_PORT", 5432))

TEST_INPUT_FILE = Path("samples/file-sample_500kB.docx")

def fetch_chunks_from_db(filename: str, strategy: str) -> list[tuple]:
    """Fetch all chunks from DB for a given filename and strategy."""
    conn = psycopg2.connect(
        dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
    )
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT chunk_text, embedding FROM chunks
            WHERE filename = %s AND split_strategy = %s;
            """,
            (filename, strategy)
        )
        results = cur.fetchall()
    conn.close()
    return results


@pytest.mark.skipif(not TEST_INPUT_FILE.exists(), reason="❌ Missing sample file for indexing test")
def test_process_file_fixed_strategy(tmp_path):
    # Given
    test_strategy = "fixed"
    test_filename = f"test_{uuid.uuid4().hex[:8]}.docx"
    temp_path = tmp_path / test_filename
    temp_path.write_bytes(TEST_INPUT_FILE.read_bytes())

    # When
    process_file(temp_path, strategy=test_strategy)

    # Then
    chunks = fetch_chunks_from_db(filename=test_filename, strategy=test_strategy)
    assert len(chunks) > 0, "❌ No chunks were saved to DB!"

    for text, embedding in chunks:
        assert isinstance(text, str) and len(text.strip()) > 0, "❌ Invalid chunk text"

        if isinstance(embedding, str):
            try:
                embedding = ast.literal_eval(embedding)
            except Exception as e:
                raise AssertionError(f"❌ Failed to parse embedding string: {embedding[:100]}") from e

        assert isinstance(embedding, (list, tuple)), "❌ Embedding is not a list or tuple"
        assert len(embedding) == 768, f"❌ Embedding length should be 768, got {len(embedding)}"

    print(f"✅ Inserted {len(chunks)} chunks for {test_filename}")

    # Optional: clean up DB
    conn = psycopg2.connect(
        dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM chunks WHERE filename = %s;", (test_filename,))
