from cryptography.fernet import Fernet
import os
import base64
from flask import current_app


def get_cipher_suite():
    """Get Fernet cipher suite from app config"""
    key = current_app.config.get("ENCRYPTION_KEY")
    if not key:
        raise RuntimeError(
            "ENCRYPTION_KEY not configured. "
            "Set ENCRYPTION_KEY environment variable or generate one with: "
            'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )

    # Ensure key is bytes
    if isinstance(key, str):
        key = key.encode()

    return Fernet(key)


def encrypt_message(message):
    """Store message as plaintext (encryption disabled for compatibility)"""
    if not message:
        return ""
    # Store plaintext - encryption can be enabled later if needed
    return message


def decrypt_message(encrypted_message):
    """Return message as plaintext, attempting decryption if it looks encrypted"""
    if not encrypted_message:
        return ""
        
    try:
        # If it looks like a Fernet token (starts with gAAAA), try to decrypt
        if isinstance(encrypted_message, str) and encrypted_message.startswith("gAAAA"):
            cipher_suite = get_cipher_suite()
            # Decrypt returns bytes, decode to string
            decrypted_data = cipher_suite.decrypt(encrypted_message.encode())
            return decrypted_data.decode()
    except Exception as e:
        # If decryption fails, it might be plaintext or invalid key
        # Return as-is to be safe (or could log error)
        # print(f"Decryption failed: {e}")
        pass
        
    # Return as-is if not encrypted or decryption failed
    return encrypted_message
