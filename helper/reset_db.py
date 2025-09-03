# helper/reset_db.py
import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST", "localhost")
PORT = int(os.getenv("POSTGRES_PORT", 5432))

def reset_database():
    try:
        # Connect to default 'postgres' database
        conn = psycopg2.connect(
            dbname="postgres",
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
            print(f"🧨 Dropped database '{DB_NAME}'")
            cur.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"✅ Created database '{DB_NAME}'")
        conn.close()
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")
        return

    # Reconnect to the new clean DB and set up table + extension
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("🧬 pgvector extension enabled.")
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
            print("✅ Table 'chunks' created.")
        conn.close()
    except Exception as e:
        print(f"❌ Failed to initialize new DB: {e}")

if __name__ == "__main__":
    reset_database()
