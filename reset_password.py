from database import get_db
from utils import hash_password

def reset_password(email, new_password):
    db = get_db()
    password_hash = hash_password(new_password)
    
    db.execute('UPDATE users SET password_hash = ? WHERE email = ?', (password_hash, email))
    db.commit()
    print(f"Password for {email} reset successfully.")

if __name__ == "__main__":
    reset_password('test@example.com', 'password123')
