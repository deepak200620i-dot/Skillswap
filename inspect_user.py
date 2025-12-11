
from sqlalchemy import create_engine, text
import os

# Database Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "database", "skillswap.db")}'

engine = create_engine(DATABASE_URL)

def check_shkachu():
    with engine.connect() as conn:
        try:
            print("Searching for user 'Shkachu'...")
            # Search by name (case insensitive)
            query = text("SELECT id, full_name, email, profile_picture FROM users WHERE full_name LIKE :name")
            result = conn.execute(query, {"name": "%Shkachu%"}).fetchall()
            
            if not result:
                print("User not found.")
            else:
                for row in result:
                    print(f"ID: {row.id}")
                    print(f"Name: {row.full_name}")
                    print(f"Email: {row.email}")
                    print(f"Profile Picture DB Value: '{row.profile_picture}'")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_shkachu()
