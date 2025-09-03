# helper/database.py
import os
import logging
import psycopg2
import numpy as np
from psycopg2 import pool
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, register_adapter, AsIs
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables from .env
load_dotenv()
log = logging.getLogger(__name__)

DB_NAME = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST", "localhost")
PORT = int(os.getenv("POSTGRES_PORT", 5432))

# Set up connection pool (singleton)
try:
    _pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=5,
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    log.info("✅ Connection pool created.")
except Exception as e:
    log.exception("❌ Failed to initialize connection pool.")
    raise


def get_connection():
    """
    Retrieves a connection from the pool and registers pgvector extension.

    Returns:
        connection (psycopg2.extensions.connection): 
            A live PostgreSQL connection with pgvector support.

    Raises:
        Exception: If a connection could not be obtained from the pool.
    """
    conn = _pool.getconn()
    register_vector(conn)
    return conn


def release_connection(conn):
    """
    Returns a database connection back to the connection pool.

    Args:
        conn (psycopg2.extensions.connection): 
            The connection object to return to the pool.
    """
    if conn:
        _pool.putconn(conn)


def insert_chunk(chunk_text: str, embedding: np.ndarray, filename: str, strategy: str):
    """
    Inserts a single chunk into the 'chunks' table.
    """
    try:
        with pooled_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO chunks (chunk_text, embedding, filename, split_strategy)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (chunk_text or "", embedding, filename or "unknown", strategy or "unspecified")
                )
                conn.commit()
    except Exception as e:
        log.exception("❌ Failed to insert chunk.")


def check_connection():
    """
    Checks the ability to connect to the database and prints the version.

    Returns:
        None
    """
    try:
        with pooled_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"🧠 Connected to: {version[0]}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")


def create_database():
    """
    Creates the target database if it does not already exist.

    Returns:
        None

    Notes:
        This function connects to the default 'postgres' DB to create a new one.
    """
    try:
        conn = psycopg2.connect(dbname="postgres", user=USER, password=PASSWORD, host=HOST, port=PORT)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(f"CREATE DATABASE {DB_NAME};")
                print(f"✅ Database '{DB_NAME}' created.")
            else:
                print(f"ℹ️ Database '{DB_NAME}' already exists.")
        conn.close()
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        exit(1)


def create_table():
    """
    Creates the 'chunks' table with required schema, including the pgvector extension.

    Returns:
        None

    Notes:
        - Enables the 'vector' extension if missing.
        - Creates table only if it does not already exist.
    """
    try:
        with pooled_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    print("🧬 pgvector extension enabled.")
                except Exception as e:
                    print(f"❌ Failed to enable pgvector: {e}")
                    print("💡 Tip: Make sure you're connected to the Docker container with pgvector pre-installed.")
                    exit(1)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chunks (
                        id SERIAL PRIMARY KEY,
                        chunk_text TEXT NOT NULL,
                        embedding VECTOR(768),
                        filename TEXT,
                        split_strategy TEXT,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                print("✅ Table 'chunks' created or already exists.")
    except Exception as e:
        print(f"❌ Failed to create table: {e}")


def adapt_list(lst):
    """
    Adapts Python list to SQL-compatible array format.

    Args:
        lst (list): A Python list.

    Returns:
        AsIs: A SQL-compatible representation for array.
    """
    return AsIs(f"ARRAY{lst}")


register_adapter(list, adapt_list)





@contextmanager
def pooled_connection():
    """
    Context manager that provides a pooled PostgreSQL connection
    and ensures it's returned to the pool after use.

    Usage:
        with pooled_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(...)

    Yields:
        psycopg2.extensions.connection: A live database connection.
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        release_connection(conn)

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     check_connection()
#     create_database()
#     create_table()
