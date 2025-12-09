"""
Error handlers and middleware for the SkillSwap application.
Provides centralized error handling and request logging.
"""

from flask import jsonify
from utils.logging_helper import log_error, log_request, log_security_event
from werkzeug.exceptions import HTTPException
import json


class APIError(Exception):
    """Custom API Error class"""

    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Convert error to dictionary"""
        rv = dict(self.payload or ())
        rv["error"] = self.message
        return rv


def register_error_handlers(app):
    """Register error handlers with Flask app"""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors"""
        log_error(f"API Error: {error.message}", status_code=error.status_code)
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request"""
        log_error(f"Bad Request: {error}")
        return jsonify({"error": "Bad request. Please check your input."}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized"""
        log_security_event("Unauthorized Access Attempt", details=str(error))
        return (
            jsonify({"error": "Unauthorized. Please provide valid credentials."}),
            401,
        )

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden"""
        log_security_event("Forbidden Access Attempt", details=str(error))
        return (
            jsonify(
                {
                    "error": "Forbidden. You do not have permission to access this resource."
                }
            ),
            403,
        )

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found"""
        log_error(f"Resource Not Found: {error}")
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Too Many Requests (Rate Limit)"""
        log_security_event("Rate Limit Exceeded", details=str(error))
        return jsonify({"error": "Too many requests. Please try again later."}), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        log_error(f"Internal Server Error: {error}", exception=error)
        return jsonify({"error": "Internal server error. Please try again later."}), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle generic HTTP exceptions"""
        log_error(f"HTTP Exception: {error}")
        return jsonify({"error": str(error)}), getattr(error, "code", 500)

    @app.errorhandler(Exception)
    def handle_general_exception(error):
        """Handle uncaught exceptions"""
        log_error(f"Uncaught Exception: {error}", exception=error)
        return (
            jsonify({"error": "An unexpected error occurred. Please try again later."}),
            500,
        )


def register_request_logging(app):
    """Register request/response logging middleware"""

    @app.before_request
    def log_request_start():
        """Log incoming request"""
        from flask import request

        # Store request start time
        import time

        request.start_time = time.time()

        # Extract user info from token if available
        user_id = None
        if "Authorization" in request.headers:
            try:
                from utils.auth_helper import decode_token

                auth_header = request.headers["Authorization"]
                token = auth_header.split(" ")[1] if " " in auth_header else None
                if token:
                    payload = decode_token(token)
                    if payload:
                        user_id = payload.get("user_id")
            except:
                pass

        log_request(request.method, request.path, user_id=user_id)

    @app.after_request
    def log_request_end(response):
        """Log request completion"""
        from flask import request
        import time

        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time
            log_request(request.method, request.path, status_code=response.status_code)

        return response
