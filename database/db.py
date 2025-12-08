import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

# Database Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Default to SQLite for local development, allow env var for production
DATABASE_URL = os.environ.get(
    "DATABASE_URL", f'sqlite:///{os.path.join(BASE_DIR, "skillswap.db")}'
)

# Handle "postgres://" to "postgresql://" fix for Render
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Handle "mysql://" to "mysql+pymysql://" for explicit driver usage
if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Fix: Remove 'ssl-mode' from query parameters as it causes errors with pymysql
if DATABASE_URL and "ssl-mode" in DATABASE_URL:
    try:
        if "?" in DATABASE_URL:
            base_url, query_args = DATABASE_URL.split("?", 1)
            params = query_args.split("&")
            # Filter out ssl-mode param which is not supported by pymysql direct args
            valid_params = [p for p in params if not p.startswith("ssl-mode=")]

            if valid_params:
                DATABASE_URL = f"{base_url}?{'&'.join(valid_params)}"
            else:
                DATABASE_URL = base_url
    except Exception as e:
        print(f"Warning: Error parsing DATABASE_URL: {e}")

# Create Engine
engine = create_engine(DATABASE_URL, echo=False)

# Create Session (Thread-safe)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db():
    """Returns a database connection object (SQLAlchemy)"""
    # Using connection for direct SQL execution to match previous pattern
    # but using SQLAlchemy's robust execution engine
    connection = engine.connect()
    return connection


def _get_db_dialect():
    """Determine the database dialect from DATABASE_URL"""
    if "postgresql" in DATABASE_URL:
        return "postgresql"
    elif "mysql" in DATABASE_URL:
        return "mysql"
    else:
        return "sqlite"


def _convert_statement_to_dialect(statement, dialect):
    """Convert SQL statement to target database dialect"""
    stmt = statement.strip()

    if dialect == "postgresql":
        # PostgreSQL conversions
        stmt = stmt.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        stmt = stmt.replace("DATETIME", "TIMESTAMP")
        stmt = stmt.replace("BOOLEAN", "BOOLEAN")
        stmt = stmt.replace(
            "INSERT OR IGNORE", "INSERT"
        )  # Use ON CONFLICT in real code, but this is safer
        stmt = stmt.replace("VARCHAR(255)", "VARCHAR(255)")
    elif dialect == "mysql":
        # MySQL conversions
        stmt = stmt.replace("AUTOINCREMENT", "AUTO_INCREMENT")
        stmt = stmt.replace(
            "INTEGER PRIMARY KEY AUTO_INCREMENT", "INT AUTO_INCREMENT PRIMARY KEY"
        )
        stmt = stmt.replace(
            "INTEGER PRIMARY KEY AUTOINCREMENT", "INT AUTO_INCREMENT PRIMARY KEY"
        )
        stmt = stmt.replace("INSERT OR IGNORE", "INSERT IGNORE")
        stmt = stmt.replace("CREATE INDEX IF NOT EXISTS", "CREATE INDEX")
        stmt = stmt.replace("UNIQUE(", "UNIQUE KEY idx_unique (")
        stmt = stmt.replace("CHECK(", "")  # MySQL has limited CHECK support
    # SQLite stays mostly as-is

    return stmt


def init_db():
    """Initialize the database with schema"""
    import logging

    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

    if not os.path.exists(SCHEMA_PATH):
        print(f"Schema file not found at: {SCHEMA_PATH}")
        return

    db_type = _get_db_dialect()
    print(f"Initializing {db_type} database...")

    try:
        with engine.connect() as conn:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()

                # Split statements by semicolon
                statements = [s.strip() for s in schema_sql.split(";") if s.strip()]

                trans = conn.begin()
                try:
                    for statement in statements:
                        # Convert statement to target dialect
                        converted_stmt = _convert_statement_to_dialect(
                            statement, db_type
                        )

                        try:
                            conn.execute(text(converted_stmt))
                        except Exception as stmt_error:
                            # Log but continue - some statements might fail on existing tables
                            error_msg = str(stmt_error)
                            # Ignore table already exists errors
                            if (
                                "already exists" not in error_msg
                                and "Duplicate" not in error_msg
                            ):
                                print(
                                    f"Warning executing: {converted_stmt[:60]}... -> {error_msg}"
                                )

                    trans.commit()
                    print("✓ Database initialized successfully!")
                except Exception as trans_error:
                    trans.rollback()
                    raise trans_error

    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise


def close_db(e=None):
    """Closes the database session"""
    db_session.remove()
