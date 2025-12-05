from flask import Blueprint, request, jsonify
from database import get_db
from utils import token_required, sanitize_input
from utils.encryption import encrypt_message, decrypt_message

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    """Get all conversations for the current user"""
    try:
        user_id = current_user['user_id']
        db = get_db()
        
        # Fetch conversations with the other user's details
        query = '''
            SELECT c.id, c.updated_at,
                   u.id as other_user_id, u.full_name, u.profile_picture,
                   (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message,
                   (SELECT created_at FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message_time,
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id AND sender_id != ? AND is_read = 0) as unread_count
            FROM conversations c
            JOIN users u ON (c.user1_id = u.id OR c.user2_id = u.id)
            WHERE (c.user1_id = ? OR c.user2_id = ?) AND u.id != ?
            ORDER BY c.updated_at DESC
        '''
        
        conversations = db.execute(query, (user_id, user_id, user_id, user_id)).fetchall()
        
        result = []
        for conv in conversations:
            # Decrypt last message
            last_msg = conv['last_message']
            if last_msg:
                decrypted_msg = decrypt_message(last_msg)
            else:
                decrypted_msg = ""
                
            result.append({
                'id': conv['id'],
                'other_user': {
                    'id': conv['other_user_id'],
                    'full_name': conv['full_name'],
                    'profile_picture': conv['profile_picture']
                },
                'last_message': decrypted_msg,
                'last_message_time': conv['last_message_time'],
                'unread_count': conv['unread_count']
            })
            
        return jsonify({'conversations': result}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch conversations: {str(e)}'}), 500

@chat_bp.route('/<int:conversation_id>/messages', methods=['GET'])
@token_required
def get_messages(current_user, conversation_id):
    """Get messages for a specific conversation"""
    try:
        user_id = current_user['user_id']
        db = get_db()
        
        # Verify user is part of the conversation
        conv = db.execute(
            'SELECT id FROM conversations WHERE id = ? AND (user1_id = ? OR user2_id = ?)',
            (conversation_id, user_id, user_id)
        ).fetchone()
        
        if not conv:
            return jsonify({'error': 'Conversation not found or access denied'}), 404
            
        # Mark messages as read
        db.execute(
            'UPDATE messages SET is_read = 1 WHERE conversation_id = ? AND sender_id != ?',
            (conversation_id, user_id)
        )
        db.commit()
        
        # Fetch messages
        messages = db.execute(
            'SELECT id, sender_id, content, created_at, is_read FROM messages WHERE conversation_id = ? ORDER BY created_at ASC',
            (conversation_id,)
        ).fetchall()
        
        result = []
        for msg in messages:
            result.append({
                'id': msg['id'],
                'sender_id': msg['sender_id'],
                'content': decrypt_message(msg['content']),
                'created_at': msg['created_at'],
                'is_read': bool(msg['is_read']),
                'is_me': msg['sender_id'] == user_id
            })
            
        return jsonify({'messages': result}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch messages: {str(e)}'}), 500

@chat_bp.route('/send', methods=['POST'])
@token_required
def send_message(current_user):
    """Send a message"""
    try:
        data = request.get_json()
        sender_id = current_user['user_id']
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        
        if not receiver_id or not content:
            return jsonify({'error': 'Receiver ID and content are required'}), 400
            
        db = get_db()
        
        # Check if conversation exists
        conv = db.execute('''
            SELECT id FROM conversations 
            WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)
        ''', (sender_id, receiver_id, receiver_id, sender_id)).fetchone()
        
        if conv:
            conversation_id = conv['id']
            # Update timestamp
            db.execute('UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (conversation_id,))
        else:
            # Create new conversation
            cursor = db.execute(
                'INSERT INTO conversations (user1_id, user2_id) VALUES (?, ?)',
                (sender_id, receiver_id)
            )
            conversation_id = cursor.lastrowid
            
        # Encrypt message
        encrypted_content = encrypt_message(content)
        if not encrypted_content:
            return jsonify({'error': 'Encryption failed'}), 500
            
        # Insert message
        db.execute(
            'INSERT INTO messages (conversation_id, sender_id, content) VALUES (?, ?, ?)',
            (conversation_id, sender_id, encrypted_content)
        )
        db.commit()
        
        return jsonify({
            'message': 'Message sent',
            'conversation_id': conversation_id,
            'content': content, # Return plain text for UI update
            'created_at': 'Just now' # In real app, return DB timestamp
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to send message: {str(e)}'}), 500
