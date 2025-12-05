from flask import Blueprint, request, jsonify
from database import get_db
from utils import token_required, sanitize_input

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
        req = db.execute('SELECT * FROM swap_requests WHERE id = ?', (request_id,)).fetchone()
        
        if not req:
            return jsonify({'error': 'Request not found'}), 404
            
        if req['status'] != 'completed':
            return jsonify({'error': 'Cannot review incomplete request'}), 400
            
        # Determine who is being reviewed
        if req['sender_id'] == reviewer_id:
            reviewed_id = req['receiver_id']
        elif req['receiver_id'] == reviewer_id:
            reviewed_id = req['sender_id']
        else:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Check if review already exists
        existing = db.execute('''
            SELECT id FROM reviews 
            WHERE request_id = ? AND reviewer_id = ?
        ''', (request_id, reviewer_id)).fetchone()
        
        if existing:
            return jsonify({'error': 'Review already submitted'}), 409
            
        # Create review
        db.execute('''
            INSERT INTO reviews (reviewer_id, reviewed_id, request_id, rating, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (reviewer_id, reviewed_id, request_id, rating, comment))
        
        db.commit()
        
        return jsonify({'message': 'Review submitted successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to submit review: {str(e)}'}), 500

@reviews_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    """Get reviews for a specific user"""
    try:
        db = get_db()
        
        reviews = db.execute('''
            SELECT 
                r.id, r.rating, r.comment, r.created_at,
                u.full_name as reviewer_name, u.profile_picture as reviewer_pic
            FROM reviews r
            JOIN users u ON r.reviewer_id = u.id
            WHERE r.reviewed_id = ?
            ORDER BY r.created_at DESC
        ''', (user_id,)).fetchall()
        
        # Calculate average rating
        avg_rating = db.execute('''
            SELECT AVG(rating) as avg_rating, COUNT(*) as count
            FROM reviews
            WHERE reviewed_id = ?
        ''', (user_id,)).fetchone()
        
        return jsonify({
            'reviews': [dict(r) for r in reviews],
            'stats': {
                'average': round(avg_rating['avg_rating'] or 0, 1),
                'count': avg_rating['count']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch reviews: {str(e)}'}), 500
