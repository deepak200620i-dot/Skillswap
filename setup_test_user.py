from app import create_app
from database.db import get_db
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import sys

try:
    app = create_app()
    with app.app_context():
        db = get_db()
        # Get first user
        result = db.execute(text("SELECT id, email FROM users LIMIT 1"))
        user = result.fetchone()
        
        if user:
            u_dict = user._mapping
            user_id = u_dict['id']
            email = u_dict['email']
            
            # Update password to 'password123'
            hashed = generate_password_hash('password123')
            db.execute(text("UPDATE users SET password_hash = :p WHERE id = :id"), {"p": hashed, "id": user_id})
            db.commit()
            print(f"User: {email}")
            print("Password: password123")
        else:
            print("No users found")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
