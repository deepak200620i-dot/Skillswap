import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration"""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///skillswap.db")

    # Encryption key - generate if not provided, but warn in production
    _encryption_key = os.getenv("ENCRYPTION_KEY")
    if not _encryption_key:
        from cryptography.fernet import Fernet

        _encryption_key = Fernet.generate_key().decode("utf-8")
    ENCRYPTION_KEY = _encryption_key

    # Flask settings
    DEBUG = os.getenv("FLASK_ENV") == "development"
    TESTING = False

    # JWT settings
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours in seconds

    # File upload settings
    UPLOAD_FOLDER = "static/uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False

    # In production, ENCRYPTION_KEY MUST be set
    @property
    def ENCRYPTION_KEY(self):
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            # Fallback to generated key with warning (prevents 500 error on startup)
            import logging
            from cryptography.fernet import Fernet
            
            logging.warning("ENCRYPTION_KEY not set in production. Generating temporary key. Encrypted data will be lost on restart.")
            return Fernet.generate_key().decode("utf-8")
        return key


# Config dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
