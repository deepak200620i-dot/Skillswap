"""Quick check of seeded users"""
from database import get_db

db = get_db()

# Check for new seeded users
seeded_emails = ['alice@example.com', 'bob@example.com', 'carol@example.com', 'david@example.com', 'emma@example.com']
users = db.execute(f"SELECT id, email, full_name FROM users WHERE email IN ({','.join(['?' for _ in seeded_emails])})", seeded_emails).fetchall()

print("Seeded Users:")
for user in users:
    print(f"  ID: {user['id']}, Email: {user['email']}, Name: {user['full_name']}")
    
    # Check skills
    skills = db.execute('''
        SELECT s.name, us.proficiency_level, us.is_teaching, us.is_learning
        FROM user_skills us
        JOIN skills s ON us.skill_id = s.id
        WHERE us.user_id = ?
    ''', (user['id'],)).fetchall()
    
    if skills:
        print(f"    Skills: {len(skills)} assigned")
    else:
        print(f"    Skills: NONE (ERROR!)")

db.close()
