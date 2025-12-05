import sqlite3
import os

DATABASE_PATH = 'skillswap.db'

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row  # Access columns by name
    return db

def init_db():
    """Initialize the database with schema"""
    db = get_db()
    
    # Read and execute schema
    schema_path = os.path.join('database', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    
    db.commit()
    db.close()
    print("Database initialized successfully!")

def close_db(db):
    """Close database connection"""
    if db is not None:
        db.close()

if __name__ == '__main__':
    # Initialize database when run directly
    init_db()
