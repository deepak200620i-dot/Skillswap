from flask import Blueprint, request, jsonify
from database.db import get_db
from sqlalchemy import text

skills_bp = Blueprint('skills', __name__, url_prefix='/api/skills')

@skills_bp.route('/', methods=['GET'])
def get_all_skills():
    """Get all available skills"""
    try:
        db = get_db()
        result = db.execute(text('SELECT id, name, category, description FROM skills ORDER BY category, name'))
        skills = result.fetchall()
        
        return jsonify({
            'skills': [dict(skill._mapping) for skill in skills]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch skills: {str(e)}'}), 500
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass

@skills_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all skill categories"""
    try:
        db = get_db()
        result = db.execute(text('SELECT DISTINCT category FROM skills ORDER BY category'))
        categories = result.fetchall()
        
        return jsonify({
            'categories': [cat._mapping['category'] for cat in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch categories: {str(e)}'}), 500
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass

@skills_bp.route('/search', methods=['GET'])
def search_skills():
    """Search skills by name or category"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        
        db = get_db()
        
        if category:
            # Filter by category
            result = db.execute(
                text('SELECT id, name, category, description FROM skills WHERE category = :category ORDER BY name'),
                {'category': category}
            )
            skills = result.fetchall()
        elif query:
            # Search by name
            # Note: Postgres ILIKE is case insensitive, SQLite LIKE is case insensitive (usually). 
            # To be safe and generic, we used to use LIKE.
            # Ideally use ILIKE for Postgres but standard SQL uses LIKE.
            # We'll stick to LIKE for now.
            result = db.execute(
                text('SELECT id, name, category, description FROM skills WHERE name LIKE :query ORDER BY name'),
                {'query': f'%{query}%'}
            )
            skills = result.fetchall()
        else:
            # Return all if no filter
            result = db.execute(text('SELECT id, name, category, description FROM skills ORDER BY category, name'))
            skills = result.fetchall()
        
        return jsonify({
            'skills': [dict(skill._mapping) for skill in skills]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to search skills: {str(e)}'}), 500
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass
