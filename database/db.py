import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'skillswap.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')

def get_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()

    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"schema.sql not found at: {SCHEMA_PATH}")

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        db.executescript(f.read())

    db.commit()
    db.close()
    print("✅ Database initialized successfully!")

def close_db(db):
    if db is not None:
        db.close()

if __name__ == '__main__':
    init_db()
