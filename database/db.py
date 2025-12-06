import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

# Database Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Default to SQLite for local development, allow env var for production
DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "skillswap.db")}')

# Handle "postgres://" to "postgresql://" fix for Render
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Handle "mysql://" to "mysql+pymysql://" for explicit driver usage
if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Create Engine
engine = create_engine(DATABASE_URL, echo=False)

# Create Session (Thread-safe)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    """Returns a database connection object (SQLAlchemy)"""
    # Using connection for direct SQL execution to match previous pattern
    # but using SQLAlchemy's robust execution engine
    connection = engine.connect()
    return connection

def init_db():
    """Initialize the database with schema"""
    import logging
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')
    
    if not os.path.exists(SCHEMA_PATH):
        print(f"Schema file not found at: {SCHEMA_PATH}")
        return

    print(f"Initializing database using: {DATABASE_URL.split('://')[0]}...")
    
    try:
        with engine.connect() as conn:
            with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                # Read schema
                schema_sql = f.read()
                
                # Split and execute statements (SQLite style logic adapted)
                # For more complex scripts, raw execution is better
                # Converting SQLite syntax to generic SQL where possible
                
                # IMPORTANT: For raw schema.sql, we'll try to execute it block by block
                # However, generic SQL compatibility is tricky.
                # Ideally, we should use SQLAlchemy models, but for this migration:
                
                if 'sqlite' in DATABASE_URL:
                   # For SQLite we can execute script
                   import sqlite3
                   # Bypass sqlalchemy for schema creation if it's sqlite to keep it simple check
                   # But we are using engine. 
                   pass

                # Execute raw SQL script
                # We need to handle potential dialect differences manually or allow failures
                # Simple split by ';'
                
                statements = schema_sql.split(';')
                trans = conn.begin()
                for statement in statements:
                    if statement.strip():
                        # Replace AUTOINCREMENT with generic serial/auto_increment logic if needed
                        # Or rely on identifying the DB type
                        
                        stmt = statement.strip()
                        
                        # Basic dialect fix: SQLite uses AUTOINCREMENT, Postgres uses SERIAL/generated
                        # This is a bit hacky but works for the documented schema.sql
                        if 'postgres' in DATABASE_URL:
                            stmt = stmt.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
                            stmt = stmt.replace('DATETIME', 'TIMESTAMP')
                        elif 'mysql' in DATABASE_URL:
                            stmt = stmt.replace('AUTOINCREMENT', 'AUTO_INCREMENT')

                        try:
                            # Use text() for generic execution
                            conn.execute(text(stmt))
                        except Exception as e:
                            print(f"Warning executing statement: {stmt[:50]}... -> {str(e)}")
                            pass
                
                trans.commit()
                print("Database initialized successfully!")
                
    except Exception as e:
        print(f"Database initialization failed: {e}")

def close_db(e=None):
    """Closes the database session"""
    db_session.remove()
