import os
import io
import json
import sys
from app import create_app
from database import init_db, get_db

# Setup
app = create_app('development')
client = app.test_client()

def reproduce():
    # Initialize DB (careful not to wipe prod data if using same DB, but init_db usually creates tables if not exist)
    # In this case, init_db() executes schema.sql which might DROP tables if configured to do so.
    # Let's check schema.sql first.
    pass

if __name__ == '__main__':
    # Check schema.sql content to avoid data loss
    with open('database/schema.sql', 'r') as f:
        if 'DROP TABLE' in f.read():
            print("WARNING: schema.sql contains DROP TABLE. Skipping init_db to avoid data loss.")
            # We will just register a new user
        else:
            with app.app_context():
                init_db()

    # 1. Register User
    print("Registering user...")
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    response = client.post('/api/auth/signup', json={
        'email': email,
        'password': 'Password123!',
        'full_name': 'Test User'
    })
    
    if response.status_code != 201:
        print(f"Registration failed: {response.get_json()}")
        sys.exit(1)
        
    data = response.get_json()
    token = data['token']
    user_id = data['user']['id']
    print(f"User registered with ID: {user_id}")

    # 2. Get Profile (Initial)
    print("Fetching initial profile...")
    response = client.get(f'/api/profile/{user_id}')
    data = response.get_json()
    initial_pic = data['user']['profile_picture']
    print(f"Initial profile picture: {initial_pic}")

    # 3. Update Profile Picture
    print("Updating profile picture...")
    data = {
        'profile_picture': (io.BytesIO(b"dummy image content"), 'test.png')
    }
    response = client.put('/api/profile/update', 
                          data=data, 
                          headers={'Authorization': f'Bearer {token}'})

    print(f"Update response status: {response.status_code}")
    print(f"Update response: {response.get_json()}")

    # 4. Get Profile (After Update)
    print("Fetching profile after update...")
    response = client.get(f'/api/profile/{user_id}')
    data = response.get_json()
    updated_pic = data['user']['profile_picture']
    print(f"Updated profile picture: {updated_pic}")

    if initial_pic == updated_pic:
        print("FAIL: Profile picture URL did not change.")
    else:
        print("SUCCESS: Profile picture URL changed.")

    # 5. Update Profile Picture AGAIN
    print("Updating profile picture AGAIN...")
    data = {
        'profile_picture': (io.BytesIO(b"dummy image content 2"), 'test.png')
    }
    response = client.put('/api/profile/update', 
                          data=data, 
                          headers={'Authorization': f'Bearer {token}'})

    # 6. Get Profile (After Second Update)
    print("Fetching profile after second update...")
    response = client.get(f'/api/profile/{user_id}')
    data = response.get_json()
    updated_pic_2 = data['user']['profile_picture']
    print(f"Second updated profile picture: {updated_pic_2}")

    if updated_pic == updated_pic_2:
        print("FAIL: Profile picture URL did not change on second update.")
    else:
        print("SUCCESS: Profile picture URL changed on second update.")
