
from app import create_app
from database.db import get_db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db = get_db()
        users = db.execute(text('SELECT id, full_name, profile_picture FROM users')).fetchall()
        for u in users:
            print(f"ID: {u.id}, Name: '{u.full_name}', Pic: '{u.profile_picture}'")
    except Exception as e:
        print(e)
