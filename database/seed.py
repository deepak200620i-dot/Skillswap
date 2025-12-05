"""
Database Seeding Script
Populates the database with test users and sample data for development/testing.
"""
import sys
import os

# Add parent directory to path to import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from utils import hash_password

def seed_users():
    """Seed test users with known credentials"""
    db = get_db()
    
    test_users = [
        {
            'email': 'alice@example.com',
            'password': 'Password123!',
            'full_name': 'Alice Johnson',
            'bio': 'Full-stack developer passionate about teaching Python and web development.',
            'profile_picture': 'https://ui-avatars.com/api/?name=AJ&background=4F46E5&color=fff',
            'location': 'New York, NY',
            'availability': 'Weekends'
        },
        {
            'email': 'bob@example.com',
            'password': 'Password123!',
            'full_name': 'Bob Smith',
            'bio': 'Graphic designer looking to learn programming and share design skills.',
            'profile_picture': 'https://ui-avatars.com/api/?name=BS&background=10B981&color=fff',
            'location': 'San Francisco, CA',
            'availability': 'Evenings'
        },
        {
            'email': 'carol@example.com',
            'password': 'Password123!',
            'full_name': 'Carol Martinez',
            'bio': 'Data scientist eager to teach data analysis and learn UI/UX design.',
            'profile_picture': 'https://ui-avatars.com/api/?name=CM&background=F59E0B&color=fff',
            'location': 'Austin, TX',
            'availability': 'Flexible'
        },
        {
            'email': 'david@example.com',
            'password': 'Password123!',
            'full_name': 'David Lee',
            'bio': 'Guitar teacher and music enthusiast. Want to learn video editing.',
            'profile_picture': 'https://ui-avatars.com/api/?name=DL&background=EF4444&color=fff',
            'location': 'Seattle, WA',
            'availability': 'Afternoons'
        },
        {
            'email': 'emma@example.com',
            'password': 'Password123!',
            'full_name': 'Emma Wilson',
            'bio': 'UX designer and public speaking coach. Love helping others grow!',
            'profile_picture': 'https://ui-avatars.com/api/?name=EW&background=8B5CF6&color=fff',
            'location': 'Boston, MA',
            'availability': 'Mornings'
        }
    ]
    
    print("Seeding users...")
    user_ids = []
    
    for user in test_users:
        # Check if user already exists
        existing = db.execute('SELECT id FROM users WHERE email = ?', (user['email'],)).fetchone()
        
        if existing:
            print(f"  [!] User {user['email']} already exists (ID: {existing['id']})")
            user_ids.append(existing['id'])
        else:
            password_hash = hash_password(user['password'])
            cursor = db.execute('''
                INSERT INTO users (email, password_hash, full_name, bio, profile_picture, location, availability)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user['email'], password_hash, user['full_name'], user['bio'], 
                  user['profile_picture'], user['location'], user['availability']))
            user_ids.append(cursor.lastrowid)
            print(f"  [+] Created {user['full_name']} ({user['email']})")
    
    db.commit()
    return user_ids

def seed_user_skills(user_ids):
    """Assign skills to users"""
    db = get_db()
    
    # Get skill IDs
    skills = db.execute('SELECT id, name FROM skills').fetchall()
    skill_map = {skill['name']: skill['id'] for skill in skills}
    
    # Define user-skill relationships
    # Format: (user_index, skill_name, proficiency, is_teaching, is_learning)
    user_skills = [
        # Alice (index 0) - Full-stack developer
        (0, 'Python', 'Expert', 1, 0),
        (0, 'JavaScript', 'Expert', 1, 0),
        (0, 'Web Development', 'Expert', 1, 0),
        (0, 'Graphic Design', 'Beginner', 0, 1),
        
        # Bob (index 1) - Graphic designer
        (1, 'Graphic Design', 'Expert', 1, 0),
        (1, 'UI/UX Design', 'Intermediate', 1, 0),
        (1, 'Python', 'Beginner', 0, 1),
        (1, 'JavaScript', 'Beginner', 0, 1),
        
        # Carol (index 2) - Data scientist
        (2, 'Data Science', 'Expert', 1, 0),
        (2, 'Python', 'Expert', 1, 0),
        (2, 'UI/UX Design', 'Beginner', 0, 1),
        
        # David (index 3) - Guitar teacher
        (3, 'Guitar', 'Expert', 1, 0),
        (3, 'Video Editing', 'Beginner', 0, 1),
        (3, 'Photography', 'Intermediate', 1, 0),
        
        # Emma (index 4) - UX designer
        (4, 'UI/UX Design', 'Expert', 1, 0),
        (4, 'Public Speaking', 'Expert', 1, 0),
        (4, 'Web Development', 'Intermediate', 0, 1),
    ]
    
    print("\nSeeding user skills...")
    
    for user_idx, skill_name, proficiency, is_teaching, is_learning in user_skills:
        if user_idx >= len(user_ids):
            continue
            
        user_id = user_ids[user_idx]
        skill_id = skill_map.get(skill_name)
        
        if not skill_id:
            print(f"  [!] Skill '{skill_name}' not found")
            continue
        
        # Check if already exists
        existing = db.execute(
            'SELECT id FROM user_skills WHERE user_id = ? AND skill_id = ?',
            (user_id, skill_id)
        ).fetchone()
        
        if existing:
            print(f"  [!] Skill mapping already exists")
            continue
        
        db.execute('''
            INSERT INTO user_skills (user_id, skill_id, proficiency_level, is_teaching, is_learning)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, skill_id, proficiency, is_teaching, is_learning))
        
        action = "Teaching" if is_teaching else "Learning"
        print(f"  [+] {action}: User {user_id} - {skill_name} ({proficiency})")
    
    db.commit()

def main():
    """Main seeding function"""
    print("=" * 60)
    print("DATABASE SEEDING SCRIPT")
    print("=" * 60)
    print("\nThis will create test users with the following credentials:")
    print("  Email: alice@example.com, bob@example.com, carol@example.com, etc.")
    print("  Password: Password123! (for all test users)")
    print("\n" + "=" * 60)
    
    try:
        user_ids = seed_users()
        seed_user_skills(user_ids)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] SEEDING COMPLETED!")
        print("=" * 60)
        print("\nTest Credentials:")
        print("  alice@example.com   / Password123!")
        print("  bob@example.com     / Password123!")
        print("  carol@example.com   / Password123!")
        print("  david@example.com   / Password123!")
        print("  emma@example.com    / Password123!")
        print("\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error during seeding: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
