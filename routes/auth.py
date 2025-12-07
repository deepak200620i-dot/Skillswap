from flask import Blueprint, request, jsonify
from database.db import get_db
from utils import hash_password, verify_password, generate_token, validate_email, validate_password, sanitize_input
from extensions import limiter
from sqlalchemy import text

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
@limiter.limit("10 per day")
def signup():
    """User registration endpoint"""
    db = None
    try:
        data = request.get_json()
        
        # Validate required fields
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        full_name = sanitize_input(data.get('full_name', ''))
        
        if not email or not password or not full_name:
            return jsonify({'error': 'Email, password, and full name are required'}), 400
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user already exists
        db = get_db()
        result = db.execute(text('SELECT id FROM users WHERE email = :email'), {'email': email})
        existing_user = result.fetchone()
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = hash_password(password)
        
        # Default profile picture (UI Avatars)
        names = full_name.strip().split()
        if len(names) >= 2:
            initials = f"{names[0][0]}{names[-1][0]}"
        elif names:
            initials = names[0][:2]
        else:
            initials = "SS"
            
        default_pic = f"https://ui-avatars.com/api/?name={initials}&background=random"
        
        # Insert new user
        db.execute(
            text('INSERT INTO users (email, password_hash, full_name, profile_picture) VALUES (:email, :password_hash, :full_name, :profile_picture)'),
            {
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name,
                'profile_picture': default_pic
            }
        )
        db.commit()
        
        # Get user_id safely (cross-DB compatible)
        result = db.execute(text('SELECT id FROM users WHERE email = :email'), {'email': email})
        user = result.fetchone()
        user_id = user[0] if user else None
        
        # Generate token
        token = generate_token(user_id, email)
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'full_name': full_name
            }
        }), 201
        
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500
    finally:
        if db:
            db.close()

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("50 per hour")
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        email = sanitize_input(data.get('email', ''))
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        db = get_db()
        result = db.execute(
            text('SELECT id, email, password_hash, full_name, bio, profile_picture FROM users WHERE email = :email'),
            {'email': email}
        )
        user = result.fetchone()
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password (user is SQLAlchemy Row, access by key works)
        if not verify_password(password, user[2]): # user['password_hash'] or index 2
             # Note: Row access by string name works in SQLAlchemy 2.0 but let's be safe safely
             # user is tuple-like: id(0), email(1), password_hash(2)...
             pass
        
        # Access columns by integer index to be absolutely safe across versions if row mapping fails
        # But specifically requesting keys is better.
        # Let's use mapping access which is standard in 2.0
        row_dict = user._mapping
        
        if not verify_password(password, row_dict['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = generate_token(row_dict['id'], row_dict['email'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': row_dict['id'],
                'email': row_dict['email'],
                'full_name': row_dict['full_name'],
                'bio': row_dict['bio'],
                'profile_picture': row_dict['profile_picture']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500
    finally:
        try:
            db.close()
        except:
            pass

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user info (requires authentication)"""
    from utils import token_required
    
    @token_required
    def _get_user(current_user):
        db = None
        try:
            db = get_db()
            result = db.execute(
                text('SELECT id, email, full_name, bio, profile_picture, location, availability FROM users WHERE id = :id'),
                {'id': current_user['user_id']}
            )
            user = result.fetchone()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            row_dict = user._mapping
            
            return jsonify({
                'user': {
                    'id': row_dict['id'],
                    'email': row_dict['email'],
                    'full_name': row_dict['full_name'],
                    'bio': row_dict['bio'],
                    'profile_picture': row_dict['profile_picture'],
                    'location': row_dict['location'],
                    'availability': row_dict['availability']
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to fetch user: {str(e)}'}), 500
        finally:
            if db:
                db.close()
    
    return _get_user()
