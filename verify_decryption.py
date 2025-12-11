import sys
import os
from cryptography.fernet import Fernet
from flask import Flask

# Add current dir to path
sys.path.append(os.getcwd())

from utils.encryption import decrypt_message

def test_decryption():
    print("Running decryption tests...")
    
    app = Flask(__name__)
    # Generate a key for testing
    key = Fernet.generate_key().decode()
    app.config["ENCRYPTION_KEY"] = key
    
    with app.app_context():
        cipher = Fernet(key.encode())
        original_msg = "Secret Message"
        
        # 1. Test Encrypted Message
        encrypted = cipher.encrypt(original_msg.encode()).decode()
        print(f"Encrypted string: {encrypted[:20]}...")
        
        decrypted = decrypt_message(encrypted)
        if decrypted == original_msg:
            print("TEST 1 PASS: Encrypted message decrypted successfully")
        else:
            print(f"TEST 1 FAIL: Expected '{original_msg}', got '{decrypted}'")
            
        # 2. Test Plaintext Message
        plaintext = "Hello World"
        result = decrypt_message(plaintext)
        if result == plaintext:
            print("TEST 2 PASS: Plaintext returned as-is")
        else:
            print(f"TEST 2 FAIL: Expected '{plaintext}', got '{result}'")
            
        # 3. Test Invalid Cipher (different key)
        other_key = Fernet.generate_key()
        other_cipher = Fernet(other_key)
        encrypted_other = other_cipher.encrypt(original_msg.encode()).decode()
        
        # Should return original encrypted string (fallback)
        result_fail = decrypt_message(encrypted_other)
        if result_fail == encrypted_other:
             print("TEST 3 PASS: Invalid key handled gracefully (returned original)")
        else:
             print(f"TEST 3 FAIL: Expected original string, got '{result_fail}'")

if __name__ == "__main__":
    test_decryption()
