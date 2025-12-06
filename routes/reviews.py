from flask import Blueprint, request, jsonify
from database.db import get_db
from utils import token_required, sanitize_input
from sqlalchemy import text

reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')

@reviews_bp.route('/', methods=['POST'])
@token_required
def create_review(current_user):
    """Create a new review"""
    try:
        data = request.get_json()
        reviewer_id = current_user['user_id']
        
        request_id = data.get('request_id')
        rating = data.get('rating')
        comment = sanitize_input(data.get('comment', ''))
        
        if not request_id or not rating:
            return jsonify({'error': 'request_id and rating are required'}), 400
            
        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            
        db = get_db()
        
        # Verify request exists and is completed
        result = db.execute(text('SELECT * FROM swap_requests WHERE id = :id'), {'id': request_id})
        req = result.fetchone()
        
        if not req:
            return jsonify({'error': 'Request not found'}), 404
        
        req_dict = req._mapping
            
        if req_dict['status'] != 'completed':
            return jsonify({'error': 'Cannot review incomplete request'}), 400
            
        # Determine who is being reviewed
        if req_dict['sender_id'] == reviewer_id:
            reviewed_id = req_dict['receiver_id']
        elif req_dict['receiver_id'] == reviewer_id:
            reviewed_id = req_dict['sender_id']
        else:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Check if review already exists
        result = db.execute(text('''
            SELECT id FROM reviews 
            WHERE request_id = :request_id AND reviewer_id = :reviewer_id
        '''), {'request_id': request_id, 'reviewer_id': reviewer_id})
        existing = result.fetchone()
        
        if existing:
            return jsonify({'error': 'Review already submitted'}), 409
            
        # Create review
        db.execute(text('''
            INSERT INTO reviews (reviewer_id, reviewed_id, request_id, rating, comment)
            VALUES (:reviewer_id, :reviewed_id, :request_id, :rating, :comment)
        '''), {
            'reviewer_id': reviewer_id, 
            'reviewed_id': reviewed_id, 
            'request_id': request_id, 
            'rating': rating, 
            'comment': comment
        })
        
        db.commit()
        
        return jsonify({'message': 'Review submitted successfully'}), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to submit review: {str(e)}'}), 500
    finally:
        db.close()

@reviews_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    """Get reviews for a specific user"""
    try:
        db = get_db()
        
        result = db.execute(text('''
            SELECT 
                r.id, r.rating, r.comment, r.created_at,
                u.full_name as reviewer_name, u.profile_picture as reviewer_pic
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.id
            WHERE r.reviewed_id = :user_id
            ORDER BY r.created_at DESC
        '''), {'user_id': user_id})
        reviews = result.fetchall()
        
        # Calculate average rating
        result = db.execute(text('''
            SELECT AVG(rating) as avg_rating, COUNT(*) as count
            FROM reviews
            WHERE reviewed_id = :user_id
        '''), {'user_id': user_id})
        avg_rating = result.fetchone()
        
        avg_val = 0
        count = 0
        if avg_rating:
            avg_dict = avg_rating._mapping
            avg_val = avg_dict['avg_rating']
            count = avg_dict['count']
        
        return jsonify({
            'reviews': [dict(r._mapping) for r in reviews],
            'stats': {
                'average': round(avg_val or 0, 1),
                'count': count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch reviews: {str(e)}'}), 500
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass
