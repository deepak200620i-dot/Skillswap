from flask import Blueprint, request, jsonify
from database.db import get_db
from utils import get_profile_picture_url
from sqlalchemy import text

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
        result = db.execute(text('''
            SELECT DISTINCT
                u.id, u.full_name, u.bio, u.profile_picture, u.location, u.availability,
                us.proficiency_level,
                s.name as skill_name, s.category
            FROM users u
            JOIN user_skills us ON u.id = us.user_id
            JOIN skills s ON us.skill_id = s.id
            WHERE us.skill_id = :skill_id AND us.is_teaching = 1
            ORDER BY us.proficiency_level DESC, u.full_name
        '''), {'skill_id': skill_id})
        teachers = result.fetchall()
        
        # Process profile pictures
        teachers_list = []
        for teacher in teachers:
            teacher_dict = dict(teacher._mapping)
            teacher_dict['profile_picture'] = get_profile_picture_url(
                teacher_dict['profile_picture'], 
                teacher_dict['full_name']
            )
            teachers_list.append(teacher_dict)
        
        return jsonify({
            'teachers': teachers_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to find teachers: {str(e)}'}), 500
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass

@matching_bp.route('/find-learners', methods=['GET'])
def find_learners():
    """Find users who want to learn a specific skill"""
    try:
        skill_id = request.args.get('skill_id')
        
        if not skill_id:
            return jsonify({'error': 'skill_id parameter is required'}), 400
        
        db = get_db()
        
        # Find learners for this skill
        result = db.execute(text('''
            SELECT DISTINCT
                u.id, u.full_name, u.bio, u.profile_picture, u.location, u.availability,
                us.proficiency_level,
                s.name as skill_name, s.category
            FROM users u
            JOIN user_skills us ON u.id = us.user_id
            JOIN skills s ON us.skill_id = s.id
            WHERE us.skill_id = :skill_id AND us.is_learning = 1
            ORDER BY u.full_name
        '''), {'skill_id': skill_id})
        learners = result.fetchall()
        
        # Process profile pictures
        learners_list = []
        for learner in learners:
            learner_dict = dict(learner._mapping)
            learner_dict['profile_picture'] = get_profile_picture_url(
                learner_dict['profile_picture'], 
                learner_dict['full_name']
            )
            learners_list.append(learner_dict)
        
        return jsonify({
            'learners': learners_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to find learners: {str(e)}'}), 500
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass

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
            result = db.execute(text('''
                SELECT skill_id FROM user_skills
                WHERE user_id = :user_id AND is_learning = 1
            '''), {'user_id': user_id})
            learning_skills = result.fetchall()
            
            if not learning_skills:
                return jsonify({'recommendations': []}), 200
            
            skill_ids = [skill._mapping['skill_id'] for skill in learning_skills]
            
            # Build dynamic placeholders for IN clause
            # :s0, :s1, :s2...
            params = {'user_id': user_id}
            placeholders = []
            
            for i, sid in enumerate(skill_ids):
                param_name = f"s{i}"
                placeholders.append(f":{param_name}")
                params[param_name] = sid
            
            placeholder_str = ', '.join(placeholders)
            
            # Find teachers for these skills
            query = f'''
                SELECT DISTINCT
                    u.id, u.full_name, u.bio, u.profile_picture, u.location,
                    s.id as skill_id, s.name as skill_name, s.category,
                    us.proficiency_level
                FROM users u
                JOIN user_skills us ON u.id = us.user_id
                JOIN skills s ON us.skill_id = s.id
                WHERE us.skill_id IN ({placeholder_str})
                AND us.is_teaching = 1
                AND u.id != :user_id
                ORDER BY us.proficiency_level DESC, u.full_name
                LIMIT 20
            '''
            
            result = db.execute(text(query), params)
            recommendations = result.fetchall()
            
            # Process profile pictures
            recommendations_list = []
            for rec in recommendations:
                rec_dict = dict(rec._mapping)
                rec_dict['profile_picture'] = get_profile_picture_url(
                    rec_dict['profile_picture'], 
                    rec_dict['full_name']
                )
                recommendations_list.append(rec_dict)
            
            return jsonify({
                'recommendations': recommendations_list
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500
        finally:
            try:
                if 'db' in locals():
                    db.close()
            except:
                pass
    
    return _get_recommendations()
