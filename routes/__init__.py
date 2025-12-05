# Routes package initialization
from .auth import auth_bp
from .profile import profile_bp
from .skills import skills_bp
from .matching import matching_bp
from .requests import requests_bp
from .reviews import reviews_bp
from .chat import chat_bp

__all__ = ['auth_bp', 'profile_bp', 'skills_bp', 'matching_bp', 'requests_bp', 'reviews_bp', 'chat_bp']
