from flask import Blueprint, request, jsonify
from database import get_db

skills_bp = Blueprint('skills', __name__, url_prefix='/api/skills')

@skills_bp.route('/', methods=['GET'])
def get_all_skills():
    """Get all available skills"""
    try:
        db = get_db()
        skills = db.execute('SELECT id, name, category, description FROM skills ORDER BY category, name').fetchall()
        
        return jsonify({
            'skills': [dict(skill) for skill in skills]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch skills: {str(e)}'}), 500

@skills_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all skill categories"""
    try:
        db = get_db()
        categories = db.execute('SELECT DISTINCT category FROM skills ORDER BY category').fetchall()
        
        return jsonify({
            'categories': [cat['category'] for cat in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch categories: {str(e)}'}), 500

@skills_bp.route('/search', methods=['GET'])
def search_skills():
    """Search skills by name or category"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        
        db = get_db()
        
        if category:
            # Filter by category
            skills = db.execute(
                'SELECT id, name, category, description FROM skills WHERE category = ? ORDER BY name',
                (category,)
            ).fetchall()
        elif query:
            # Search by name
            skills = db.execute(
                'SELECT id, name, category, description FROM skills WHERE name LIKE ? ORDER BY name',
                (f'%{query}%',)
            ).fetchall()
        else:
            # Return all if no filter
            skills = db.execute('SELECT id, name, category, description FROM skills ORDER BY category, name').fetchall()
        
        return jsonify({
            'skills': [dict(skill) for skill in skills]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to search skills: {str(e)}'}), 500
