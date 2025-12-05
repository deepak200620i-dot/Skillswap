from flask import Blueprint, request, jsonify
from database.db import get_db
from utils import hash_password, verify_password, generate_token, validate_email, validate_password, sanitize_input
from extensions import limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
@limiter.limit("10 per day")
def signup():
    """User registration endpoint"""
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
        existing_user = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = hash_password(password)
        
        # Default profile picture (UI Avatars)
        # Extract initials (First letter of first name + First letter of last name)
        names = full_name.strip().split()
        if len(names) >= 2:
            initials = f"{names[0][0]}{names[-1][0]}"
        elif names:
            initials = names[0][:2]
        else:
            initials = "SS" # Default fallback
            
        default_pic = f"https://ui-avatars.com/api/?name={initials}&background=random"
        
        # Insert new user
        cursor = db.execute(
            'INSERT INTO users (email, password_hash, full_name, profile_picture) VALUES (?, ?, ?, ?)',
            (email, password_hash, full_name, default_pic)
        )
        db.commit()
        user_id = cursor.lastrowid
        
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
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

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
        user = db.execute(
            'SELECT id, email, password_hash, full_name, bio, profile_picture FROM users WHERE email = ?',
            (email,)
        ).fetchone()
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = generate_token(user['id'], user['email'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'bio': user['bio'],
                'profile_picture': user['profile_picture']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user info (requires authentication)"""
    from utils import token_required
    
    @token_required
    def _get_user(current_user):
        try:
            db = get_db()
            user = db.execute(
                'SELECT id, email, full_name, bio, profile_picture, location, availability FROM users WHERE id = ?',
                (current_user['user_id'],)
            ).fetchone()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'bio': user['bio'],
                    'profile_picture': user['profile_picture'],
                    'location': user['location'],
                    'availability': user['availability']
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to fetch user: {str(e)}'}), 500
    
    return _get_user()
