# helper/setup_db.py
import logging
from helper.database import check_connection, create_database, create_table

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🔧 Starting DB setup...")

    check_connection()
    create_database()
    create_table()

    print("✅ Setup complete.")
