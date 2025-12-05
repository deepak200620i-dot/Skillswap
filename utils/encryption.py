from cryptography.fernet import Fernet
import os
import base64
from flask import current_app

def get_cipher_suite():
    """Get Fernet cipher suite from app config"""
    key = current_app.config.get('ENCRYPTION_KEY')
    if not key:
        # Fallback for development if key is missing (NOT SECURE for production)
        # In production, this should raise an error
        print("WARNING: ENCRYPTION_KEY not set. Using a temporary key.")
        key = Fernet.generate_key()
    
    # Ensure key is bytes
    if isinstance(key, str):
        key = key.encode()
        
    return Fernet(key)

def encrypt_message(message):
    """Encrypt a message using AES-256 (Fernet)"""
    if not message:
        return ""
    
    try:
        cipher_suite = get_cipher_suite()
        encrypted_bytes = cipher_suite.encrypt(message.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

def decrypt_message(encrypted_message):
    """Decrypt a message using AES-256 (Fernet)"""
    if not encrypted_message:
        return ""
        
    try:
        cipher_suite = get_cipher_suite()
        decrypted_bytes = cipher_suite.decrypt(encrypted_message.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return "[Encrypted Message]"
