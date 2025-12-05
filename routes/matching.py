from flask import Blueprint, request, jsonify
from database.db import get_db
from utils import get_profile_picture_url

matching_bp = Blueprint('matching', __name__, url_prefix='/api/matching')

@matching_bp.route('/find-teachers', methods=['GET'])
def find_teachers():
    """Find users who teach a specific skill"""
    try:
        skill_id = request.args.get('skill_id')
        
        if not skill_id:
            return jsonify({'error': 'skill_id parameter is required'}), 400
        
        db = get_db()
        
        # Find teachers for this skill
        teachers = db.execute('''
            SELECT DISTINCT
                u.id, u.full_name, u.bio, u.profile_picture, u.location, u.availability,
                us.proficiency_level,
                s.name as skill_name, s.category
            FROM users u
            JOIN user_skills us ON u.id = us.user_id
            JOIN skills s ON us.skill_id = s.id
            WHERE us.skill_id = ? AND us.is_teaching = 1
            ORDER BY us.proficiency_level DESC, u.full_name
        ''', (skill_id,)).fetchall()
        
        # Process profile pictures
        teachers_list = []
        for teacher in teachers:
            teacher_dict = dict(teacher)
            teacher_dict['profile_picture'] = get_profile_picture_url(
                teacher['profile_picture'], 
                teacher['full_name']
            )
            teachers_list.append(teacher_dict)
        
        return jsonify({
            'teachers': teachers_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to find teachers: {str(e)}'}), 500

@matching_bp.route('/find-learners', methods=['GET'])
def find_learners():
    """Find users who want to learn a specific skill"""
    try:
        skill_id = request.args.get('skill_id')
        
        if not skill_id:
            return jsonify({'error': 'skill_id parameter is required'}), 400
        
        db = get_db()
        
        # Find learners for this skill
        learners = db.execute('''
            SELECT DISTINCT
                u.id, u.full_name, u.bio, u.profile_picture, u.location, u.availability,
                us.proficiency_level,
                s.name as skill_name, s.category
            FROM users u
            JOIN user_skills us ON u.id = us.user_id
            JOIN skills s ON us.skill_id = s.id
            WHERE us.skill_id = ? AND us.is_learning = 1
            ORDER BY u.full_name
        ''', (skill_id,)).fetchall()
        
        # Process profile pictures
        learners_list = []
        for learner in learners:
            learner_dict = dict(learner)
            learner_dict['profile_picture'] = get_profile_picture_url(
                learner['profile_picture'], 
                learner['full_name']
            )
            learners_list.append(learner_dict)
        
        return jsonify({
            'learners': learners_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to find learners: {str(e)}'}), 500

@matching_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get personalized recommendations for a user"""
    from utils import token_required
    
    @token_required
    def _get_recommendations(current_user):
        try:
            user_id = current_user['user_id']
            db = get_db()
            
            # Get skills the user wants to learn
            learning_skills = db.execute('''
                SELECT skill_id FROM user_skills
                WHERE user_id = ? AND is_learning = 1
            ''', (user_id,)).fetchall()
            
            if not learning_skills:
                return jsonify({'recommendations': []}), 200
            
            skill_ids = [skill['skill_id'] for skill in learning_skills]
            placeholders = ','.join('?' * len(skill_ids))
            
            # Find teachers for these skills
            recommendations = db.execute(f'''
                SELECT DISTINCT
                    u.id, u.full_name, u.bio, u.profile_picture, u.location,
                    s.id as skill_id, s.name as skill_name, s.category,
                    us.proficiency_level
                FROM users u
                JOIN user_skills us ON u.id = us.user_id
                JOIN skills s ON us.skill_id = s.id
                WHERE us.skill_id IN ({placeholders})
                AND us.is_teaching = 1
                AND u.id != ?
                ORDER BY us.proficiency_level DESC, u.full_name
                LIMIT 20
            ''', (*skill_ids, user_id)).fetchall()
            
            # Process profile pictures
            recommendations_list = []
            for rec in recommendations:
                rec_dict = dict(rec)
                rec_dict['profile_picture'] = get_profile_picture_url(
                    rec['profile_picture'], 
                    rec['full_name']
                )
                recommendations_list.append(rec_dict)
            
            return jsonify({
                'recommendations': recommendations_list
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500
    
    return _get_recommendations()
