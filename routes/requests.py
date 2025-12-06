from flask import Blueprint, request, jsonify
from database.db import get_db
from utils import token_required, sanitize_input, get_profile_picture_url
from sqlalchemy import text

requests_bp = Blueprint('requests', __name__, url_prefix='/api/requests')

@requests_bp.route('/', methods=['POST'])
@token_required
def create_request(current_user):
    """Create a new swap request"""
    try:
        data = request.get_json()
        sender_id = current_user['user_id']
        
        receiver_id = data.get('receiver_id')
        skill_id = data.get('skill_id')
        message = sanitize_input(data.get('message', ''))
        
        if not receiver_id or not skill_id:
            return jsonify({'error': 'receiver_id and skill_id are required'}), 400
            
        if sender_id == receiver_id:
            return jsonify({'error': 'Cannot request swap with yourself'}), 400
            
        db = get_db()
        
        # Check if request already exists
        result = db.execute(text('''
            SELECT id FROM swap_requests 
            WHERE sender_id = :sender_id AND receiver_id = :receiver_id AND skill_id = :skill_id AND status = 'pending'
        '''), {'sender_id': sender_id, 'receiver_id': receiver_id, 'skill_id': skill_id})
        existing = result.fetchone()
        
        if existing:
            return jsonify({'error': 'Pending request already exists'}), 409
            
        # Create request
        db.execute(text('''
            INSERT INTO swap_requests (sender_id, receiver_id, skill_id, message)
            VALUES (:sender_id, :receiver_id, :skill_id, :message)
        '''), {
            'sender_id': sender_id, 
            'receiver_id': receiver_id, 
            'skill_id': skill_id, 
            'message': message
        })
        
        db.commit()
        
        return jsonify({'message': 'Swap request sent successfully'}), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to create request: {str(e)}'}), 500
    finally:
        db.close()

@requests_bp.route('/', methods=['GET'])
@token_required
def get_requests(current_user):
    """Get all requests for current user"""
    try:
        user_id = current_user['user_id']
        db = get_db()
        
        # Incoming requests (others requesting me)
        result = db.execute(text('''
            SELECT 
                r.id, r.status, r.message, r.created_at,
                u.id as sender_id, u.full_name as sender_name, u.profile_picture as sender_pic,
                s.name as skill_name
            FROM swap_requests r
            JOIN users u ON r.sender_id = u.id
            JOIN skills s ON r.skill_id = s.id
            WHERE r.receiver_id = :user_id
            ORDER BY r.created_at DESC
        '''), {'user_id': user_id})
        incoming = result.fetchall()
        
        # Sent requests (I requested others)
        result = db.execute(text('''
            SELECT 
                r.id, r.status, r.message, r.created_at,
                u.id as receiver_id, u.full_name as receiver_name, u.profile_picture as receiver_pic,
                s.name as skill_name
            FROM swap_requests r
            JOIN users u ON r.receiver_id = u.id
            JOIN skills s ON r.skill_id = s.id
            WHERE r.sender_id = :user_id
            ORDER BY r.created_at DESC
        '''), {'user_id': user_id})
        sent = result.fetchall()
        
        # Process profile pictures
        incoming_list = []
        for req in incoming:
            req_dict = dict(req._mapping)
            req_dict['sender_pic'] = get_profile_picture_url(req_dict['sender_pic'], req_dict['sender_name'])
            incoming_list.append(req_dict)
        
        sent_list = []
        for req in sent:
            req_dict = dict(req._mapping)
            req_dict['receiver_pic'] = get_profile_picture_url(req_dict['receiver_pic'], req_dict['receiver_name'])
            sent_list.append(req_dict)
        
        return jsonify({
            'incoming': incoming_list,
            'sent': sent_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch requests: {str(e)}'}), 500
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass

@requests_bp.route('/<int:request_id>/status', methods=['PUT'])
@token_required
def update_status(current_user, request_id):
    """Update request status (accept/reject/complete)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        user_id = current_user['user_id']
        
        if new_status not in ['accepted', 'rejected', 'completed']:
            return jsonify({'error': 'Invalid status'}), 400
            
        db = get_db()
        
        # Get request
        result = db.execute(text('SELECT * FROM swap_requests WHERE id = :id'), {'id': request_id})
        req = result.fetchone()
        
        if not req:
            return jsonify({'error': 'Request not found'}), 404
        
        req_dict = req._mapping
            
        # Authorization checks
        if new_status in ['accepted', 'rejected']:
            # Only receiver can accept/reject
            if req_dict['receiver_id'] != user_id:
                return jsonify({'error': 'Unauthorized'}), 403
                
        elif new_status == 'completed':
            # Either party can mark as completed (simplification for MVP)
            if req_dict['sender_id'] != user_id and req_dict['receiver_id'] != user_id:
                return jsonify({'error': 'Unauthorized'}), 403
                
        # Update status
        db.execute(text('UPDATE swap_requests SET status = :status WHERE id = :id'), 
                  {'status': new_status, 'id': request_id})
        db.commit()
        
        return jsonify({'message': f'Request {new_status}'}), 200
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to update status: {str(e)}'}), 500
    finally:
        db.close()
