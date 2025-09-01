# database.py
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from psycopg2.extensions import register_adapter, AsIs
from pgvector.psycopg2 import register_vector
import numpy as np
# Load environment variables from .env
load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = int(os.getenv("POSTGRES_PORT", 5432))

def check_connection():
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT)
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"🧠 Connected to: {version[0]}")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        exit(1)

def create_database():
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
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT)
        with conn.cursor() as cur:
            # Try to enable pgvector
            try:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                print("🧬 pgvector extension enabled.")
            except Exception as e:
                print(f"❌ Failed to enable pgvector: {e}")
                print("💡 Tip: Make sure you're connected to the Docker container with pgvector pre-installed.")
                exit(1)

            # Create the table
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
        conn.close()
    except Exception as e:
        print(f"❌ Failed to create table: {e}")
        exit(1)


def adapt_list(lst):
    return AsIs(f"ARRAY{lst}")

register_adapter(list, adapt_list)

def insert_chunk(chunk_text: str, embedding: np.ndarray, filename: str, strategy: str):
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT)
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chunks (chunk_text, embedding, filename, split_strategy)
                VALUES (%s, %s, %s, %s);
                """,
                (chunk_text, embedding, filename, strategy)
            )
            conn.commit()
    except Exception as e:
        print(f"❌ Failed to insert chunk: {e}")
    finally:
        conn.close()



def get_connection():
    """
    Returns a psycopg2 connection to the Postgres database
    with pgvector registered.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        register_vector(conn)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        raise
if __name__ == "__main__":
    check_connection()
    create_database()
    create_table()
