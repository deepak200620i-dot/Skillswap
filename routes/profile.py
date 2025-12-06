from flask import Blueprint, request, jsonify
from database.db import get_db
from utils import token_required, sanitize_input
from sqlalchemy import text

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

@profile_bp.route('/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """Get user profile by ID"""
    try:
        db = get_db()
        
        # Get user info
        result = db.execute(
            text('SELECT id, email, full_name, bio, profile_picture, location, availability, created_at FROM users WHERE id = :id'),
            {'id': user_id}
        )
        user = result.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user_dict = user._mapping
        
        # Get user's skills they teach
        result = db.execute(text('''
            SELECT s.id, s.name, s.category, us.proficiency_level
            FROM skills s
            JOIN user_skills us ON s.id = us.skill_id
            WHERE us.user_id = :user_id AND us.is_teaching = 1
        '''), {'user_id': user_id})
        teaching_skills = result.fetchall()
        
        # Get user's skills they want to learn
        result = db.execute(text('''
            SELECT s.id, s.name, s.category, us.proficiency_level
            FROM skills s
            JOIN user_skills us ON s.id = us.skill_id
            WHERE us.user_id = :user_id AND us.is_learning = 1
        '''), {'user_id': user_id})
        learning_skills = result.fetchall()
        
        # Handle default profile picture for existing users
        profile_pic = user_dict['profile_picture']
        if not profile_pic or profile_pic == 'default-avatar.png':
            # Generate initials
            names = user_dict['full_name'].strip().split()
            if len(names) >= 2:
                initials = f"{names[0][0]}{names[-1][0]}"
            elif names:
                initials = names[0][:2]
            else:
                initials = "SS"
            profile_pic = f"https://ui-avatars.com/api/?name={initials}&background=random"

        return jsonify({
            'user': {
                'id': user_dict['id'],
                'email': user_dict['email'],
                'full_name': user_dict['full_name'],
                'bio': user_dict['bio'],
                'profile_picture': profile_pic,
                'location': user_dict['location'],
                'availability': user_dict['availability'],
                'created_at': user_dict['created_at']
            },
            'teaching_skills': [dict(skill._mapping) for skill in teaching_skills],
            'learning_skills': [dict(skill._mapping) for skill in learning_skills]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch profile: {str(e)}'}), 500
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass

@profile_bp.route('/update', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile (requires authentication)"""
    try:
        data = request.get_json(silent=True) or {}
        user_id = current_user['user_id']
        
        # Extract and sanitize fields
        full_name = sanitize_input(data.get('full_name'))
        bio = sanitize_input(data.get('bio'))
        location = sanitize_input(data.get('location'))
        availability = sanitize_input(data.get('availability'))
        
        if not data:
            # Try getting from form if json is empty (multipart/form-data)
            full_name = request.form.get('full_name')
            bio = request.form.get('bio')
            location = request.form.get('location')
            availability = request.form.get('availability')
            
        # Build update query dynamically
        update_fields = []
        params = {}
        
        # Handle file upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                import os
                from werkzeug.utils import secure_filename
                
                filename = secure_filename(file.filename)
                # Ensure unique filename
                import uuid
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # Save path
                upload_folder = 'static/uploads/profile_pics'
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                    
                file.save(os.path.join(upload_folder, unique_filename))
                
                # Update DB path
                update_fields.append('profile_picture = :profile_picture')
                params['profile_picture'] = f"/{upload_folder}/{unique_filename}"
        
        # Build update query dynamically
        
        if full_name:
            update_fields.append('full_name = :full_name')
            params['full_name'] = full_name
        
        if bio is not None:
            update_fields.append('bio = :bio')
            params['bio'] = bio
        
        if location:
            update_fields.append('location = :location')
            params['location'] = location
        
        if availability:
            update_fields.append('availability = :availability')
            params['availability'] = availability
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        # Add user_id to params
        params['id'] = user_id
        
        # Update user
        db = get_db()
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = :id"
        db.execute(text(query), params)
        db.commit()
        
        # Fetch updated user
        result = db.execute(
            text('SELECT id, email, full_name, bio, profile_picture, location, availability FROM users WHERE id = :id'),
            {'id': user_id}
        )
        updated_user = result.fetchone()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': dict(updated_user._mapping)
        }), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500
    finally:
        db.close()

@profile_bp.route('/skills', methods=['POST'])
@token_required
def add_skill(current_user):
    """Add a skill to user's profile"""
    try:
        data = request.get_json()
        user_id = current_user['user_id']
        
        skill_id = data.get('skill_id')
        proficiency_level = data.get('proficiency_level', 'Beginner')
        is_teaching = data.get('is_teaching', False)
        is_learning = data.get('is_learning', False)
        
        # Validate
        if not skill_id:
            return jsonify({'error': 'skill_id is required'}), 400
        
        if proficiency_level not in ['Beginner', 'Intermediate', 'Expert']:
            return jsonify({'error': 'Invalid proficiency level'}), 400
        
        if not is_teaching and not is_learning:
            return jsonify({'error': 'Must specify is_teaching or is_learning'}), 400
        
        db = get_db()
        
        # Check if skill exists
        result = db.execute(text('SELECT id FROM skills WHERE id = :id'), {'id': skill_id})
        skill = result.fetchone()
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        # Check if user already has this skill
        result = db.execute(
            text('SELECT id FROM user_skills WHERE user_id = :user_id AND skill_id = :skill_id'),
            {'user_id': user_id, 'skill_id': skill_id}
        )
        existing = result.fetchone()
        
        if existing:
            # Update existing skill
            db.execute(text('''
                UPDATE user_skills 
                SET proficiency_level = :level, is_teaching = :teaching, is_learning = :learning
                WHERE user_id = :user_id AND skill_id = :skill_id
            '''), {
                'level': proficiency_level,
                'teaching': is_teaching,
                'learning': is_learning,
                'user_id': user_id,
                'skill_id': skill_id
            })
        else:
            # Insert new skill
            db.execute(text('''
                INSERT INTO user_skills (user_id, skill_id, proficiency_level, is_teaching, is_learning)
                VALUES (:user_id, :skill_id, :level, :teaching, :learning)
            '''), {
                'user_id': user_id,
                'skill_id': skill_id,
                'level': proficiency_level,
                'teaching': is_teaching,
                'learning': is_learning
            })
        
        db.commit()
        
        return jsonify({'message': 'Skill added successfully'}), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to add skill: {str(e)}'}), 500
    finally:
        db.close()

@profile_bp.route('/skills/<int:skill_id>', methods=['DELETE'])
@token_required
def remove_skill(current_user, skill_id):
    """Remove a skill from user's profile"""
    try:
        user_id = current_user['user_id']
        
        db = get_db()
        db.execute(text('DELETE FROM user_skills WHERE user_id = :user_id AND skill_id = :skill_id'), 
                  {'user_id': user_id, 'skill_id': skill_id})
        db.commit()
        
        return jsonify({'message': 'Skill removed successfully'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to remove skill: {str(e)}'}), 500
    finally:
        db.close()
