from flask import Blueprint, request, jsonify
from database.db import get_db
from utils import token_required, sanitize_input
from utils.encryption import encrypt_message, decrypt_message
from extensions import limiter
from sqlalchemy import text

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/conversations', methods=['GET'])
@token_required
@limiter.limit("1 per second")
def get_conversations(current_user):
    """Get all conversations for the current user"""
    try:
        user_id = current_user['user_id']
        db = get_db()
        
        # Fetch conversations with the other user's details
        # Note: SQLAlchemy execute returns rows, which can be accessed by mapping
        query = '''
            SELECT c.id, c.updated_at,
                   u.id as other_user_id, u.full_name, u.profile_picture,
                   (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message,
                   (SELECT created_at FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message_time,
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id AND sender_id != :user_id AND is_read = 0) as unread_count
            FROM conversations c
            JOIN users u ON (c.user1_id = u.id OR c.user2_id = u.id)
            WHERE (c.user1_id = :user_id OR c.user2_id = :user_id) AND u.id != :user_id
            ORDER BY c.updated_at DESC
        '''
        
        # Need to provide user_id multiple times if named params were not used, but named params handle it nicely
        result = db.execute(text(query), {'user_id': user_id})
        conversations = result.fetchall()
        
        result_list = []
        for conv in conversations:
            conv_dict = conv._mapping
            # Decrypt last message
            last_msg = conv_dict['last_message']
            if last_msg:
                decrypted_msg = decrypt_message(last_msg)
            else:
                decrypted_msg = ""
                
            result_list.append({
                'id': conv_dict['id'],
                'other_user': {
                    'id': conv_dict['other_user_id'],
                    'full_name': conv_dict['full_name'],
                    'profile_picture': conv_dict['profile_picture']
                },
                'last_message': decrypted_msg,
                'last_message_time': conv_dict['last_message_time'],
                'unread_count': conv_dict['unread_count']
            })
            
        return jsonify({'conversations': result_list}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch conversations: {str(e)}'}), 500
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass

@chat_bp.route('/<int:conversation_id>/messages', methods=['GET'])
@token_required
@limiter.limit("1 per second")
def get_messages(current_user, conversation_id):
    """Get messages for a specific conversation"""
    try:
        user_id = current_user['user_id']
        db = get_db()
        
        # Verify user is part of the conversation
        result = db.execute(
            text('SELECT id FROM conversations WHERE id = :conv_id AND (user1_id = :user_id OR user2_id = :user_id)'),
            {'conv_id': conversation_id, 'user_id': user_id}
        )
        conv = result.fetchone()
        
        if not conv:
            return jsonify({'error': 'Conversation not found or access denied'}), 404
            
        # Mark messages as read
        db.execute(
            text('UPDATE messages SET is_read = 1 WHERE conversation_id = :conv_id AND sender_id != :user_id'),
            {'conv_id': conversation_id, 'user_id': user_id}
        )
        db.commit()
        
        # Fetch messages
        result = db.execute(
            text('SELECT id, sender_id, content, created_at, is_read FROM messages WHERE conversation_id = :conv_id ORDER BY created_at ASC'),
            {'conv_id': conversation_id}
        )
        messages = result.fetchall()
        
        result_list = []
        for msg in messages:
            msg_dict = msg._mapping
            result_list.append({
                'id': msg_dict['id'],
                'sender_id': msg_dict['sender_id'],
                'content': decrypt_message(msg_dict['content']),
                'created_at': msg_dict['created_at'],
                'is_read': bool(msg_dict['is_read']),
                'is_me': msg_dict['sender_id'] == user_id
            })
            
        return jsonify({'messages': result_list}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch messages: {str(e)}'}), 500
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass

@chat_bp.route('/send', methods=['POST'])
@token_required
@limiter.limit("1 per second")
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
        result = db.execute(text('''
            SELECT id FROM conversations 
            WHERE (user1_id = :sender_id AND user2_id = :receiver_id) OR (user1_id = :receiver_id AND user2_id = :sender_id)
        '''), {'sender_id': sender_id, 'receiver_id': receiver_id})
        conv = result.fetchone()
        
        if conv:
            conv_dict = conv._mapping
            conversation_id = conv_dict['id']
            # Update timestamp
            # use CURRENT_TIMESTAMP for SQLite/Postgres/MySQL
            db.execute(text('UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = :id'), {'id': conversation_id})
        else:
            # Create new conversation
            db.execute(
                text('INSERT INTO conversations (user1_id, user2_id) VALUES (:sender_id, :receiver_id)'),
                {'sender_id': sender_id, 'receiver_id': receiver_id}
            )
            db.commit()
            
            # Get ID of created conversation
            # Safe way for cross-DB compatibility
            result = db.execute(text('''
                SELECT id FROM conversations 
                WHERE (user1_id = :sender_id AND user2_id = :receiver_id) OR (user1_id = :receiver_id AND user2_id = :sender_id)
                ORDER BY id DESC LIMIT 1
            '''), {'sender_id': sender_id, 'receiver_id': receiver_id})
            new_conv = result.fetchone()
            conversation_id = new_conv._mapping['id'] if new_conv else None
            
        # Encrypt message
        encrypted_content = encrypt_message(content)
        if not encrypted_content:
            return jsonify({'error': 'Encryption failed'}), 500
            
        # Insert message
        db.execute(
            text('INSERT INTO messages (conversation_id, sender_id, content) VALUES (:conv_id, :sender_id, :content)'),
            {'conv_id': conversation_id, 'sender_id': sender_id, 'content': encrypted_content}
        )
        db.commit()
        
        return jsonify({
            'message': 'Message sent',
            'conversation_id': conversation_id,
            'content': content, # Return plain text for UI update
            'created_at': 'Just now' # In real app, return DB timestamp
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to send message: {str(e)}'}), 500
    finally:
        db.close()
