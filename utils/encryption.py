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
    """Encrypt a message using AES-256 (Fernet)"""
    if not message:
        return ""

    try:
        cipher_suite = get_cipher_suite()
        encrypted_bytes = cipher_suite.encrypt(message.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")
    except Exception as e:
        print(f"Encryption error: {e}")
        raise


def decrypt_message(encrypted_message):
    """Decrypt a message using AES-256 (Fernet)"""
    if not encrypted_message:
        return ""

    try:
        cipher_suite = get_cipher_suite()
        decrypted_bytes = cipher_suite.decrypt(encrypted_message.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        print(f"Decryption error: {e}")
        return "[Decryption Failed]"
