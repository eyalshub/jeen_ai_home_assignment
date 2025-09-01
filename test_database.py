# tests/test_database.py

import os
import psycopg2
import pytest
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = int(os.getenv("POSTGRES_PORT", 5432))


@pytest.fixture(scope="module")
def db_connection():
    """Connect to the main DB and yield cursor + connection."""
    conn = psycopg2.connect(
        dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
    )
    cur = conn.cursor()
    yield cur, conn
    conn.commit()
    cur.close()
    conn.close()


def test_table_exists(db_connection):
    cur, _ = db_connection
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'chunks'
        );
    """)
    exists = cur.fetchone()[0]
    assert exists, "❌ Table 'chunks' does not exist"


def test_insert_sample_row(db_connection):
    cur, _ = db_connection

    cur.execute("""
        INSERT INTO chunks (chunk_text, embedding, filename, split_strategy)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (
        "Sample text", [0.1]*768, "test.txt", "by_sentence"
    ))

    inserted_id = cur.fetchone()[0]
    assert isinstance(inserted_id, int), "❌ Failed to insert row"

    # Optional: cleanup (delete row after test)
    cur.execute("DELETE FROM chunks WHERE id = %s;", (inserted_id,))
