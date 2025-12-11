
from app import create_app
from database.db import get_db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db = get_db()
        # ID 2 is Shkachu based on previous list_users.py
        new_path = "/static/uploads/profile_pics/shkachu_fixed.png"
        print(f"Updating Shkachu (ID 2) profile pic to: {new_path}")
        db.execute(text("UPDATE users SET profile_picture = :p WHERE id = 2"), {"p": new_path})
        db.commit()
        print("Update successful.")
    except Exception as e:
        print(f"Error: {e}")
