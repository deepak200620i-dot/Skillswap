from database.db import init_db, get_db
from utils import hash_password

# Step 1: create tables
init_db()  # <--- this ensures tables exist

db = get_db()

# Step 2: insert users
email = "test@render.com"
password = "Test1234"
full_name = "Render Test"
password_hash = hash_password(password)

existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
if not existing:
    db.execute(
        'INSERT INTO users (email, password_hash, full_name, profile_picture) VALUES (?, ?, ?, ?)',
        (email, password_hash, full_name, "https://ui-avatars.com/api/?name=RT")
    )
    db.commit()
    print("✅ Test user created")
else:
    print("ℹ️ Test user already exists")

db.close()
