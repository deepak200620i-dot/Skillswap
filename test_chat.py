import unittest
import json
from app import create_app
from database import init_db, get_db
from utils.encryption import encrypt_message, decrypt_message

class ChatTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Use in-memory DB for testing or separate test DB
        # For simplicity in this environment, we'll use the existing DB but be careful
        # Actually, let's just use the existing DB but create new test users
        
    def tearDown(self):
        self.app_context.pop()

    def test_encryption(self):
        """Test AES-256 encryption"""
        original = "Secret Message"
        encrypted = encrypt_message(original)
        decrypted = decrypt_message(encrypted)
        
        self.assertNotEqual(original, encrypted)
        self.assertEqual(original, decrypted)
        print("Encryption test passed!")

    def test_chat_flow(self):
        """Test sending and receiving messages"""
        import uuid
        
        # Register User A
        email_a = f"user_a_{uuid.uuid4().hex[:8]}@example.com"
        res_a = self.client.post('/api/auth/signup', json={
            'email': email_a,
            'password': 'Password123!',
            'full_name': 'User A'
        })
        token_a = res_a.get_json()['token']
        id_a = res_a.get_json()['user']['id']
        
        # Register User B
        email_b = f"user_b_{uuid.uuid4().hex[:8]}@example.com"
        res_b = self.client.post('/api/auth/signup', json={
            'email': email_b,
            'password': 'Password123!',
            'full_name': 'User B'
        })
        token_b = res_b.get_json()['token']
        id_b = res_b.get_json()['user']['id']
        
        # User A sends message to User B
        msg_content = "Hello User B!"
        res_send = self.client.post('/api/chat/send', 
            headers={'Authorization': f'Bearer {token_a}'},
            json={'receiver_id': id_b, 'content': msg_content}
        )
        self.assertEqual(res_send.status_code, 201)
        conv_id = res_send.get_json()['conversation_id']
        
        # Verify message in DB is encrypted
        db = get_db()
        msg_row = db.execute('SELECT content FROM messages WHERE conversation_id = ?', (conv_id,)).fetchone()
        self.assertNotEqual(msg_row['content'], msg_content)
        self.assertEqual(decrypt_message(msg_row['content']), msg_content)
        print("Message stored encrypted in DB.")
        
        # User B fetches conversations
        res_conv = self.client.get('/api/chat/conversations', 
            headers={'Authorization': f'Bearer {token_b}'}
        )
        self.assertEqual(res_conv.status_code, 200)
        convs = res_conv.get_json()['conversations']
        self.assertEqual(len(convs), 1)
        self.assertEqual(convs[0]['last_message'], msg_content)
        self.assertEqual(convs[0]['unread_count'], 1)
        
        # User B fetches messages
        res_msgs = self.client.get(f'/api/chat/{conv_id}/messages', 
            headers={'Authorization': f'Bearer {token_b}'}
        )
        self.assertEqual(res_msgs.status_code, 200)
        msgs = res_msgs.get_json()['messages']
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]['content'], msg_content)
        
        print("Chat flow test passed!")

if __name__ == '__main__':
    unittest.main()
