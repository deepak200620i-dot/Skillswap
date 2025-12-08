from flask import Blueprint, request, jsonify
from database.db import get_db
from utils import (
    hash_password,
    verify_password,
    generate_token,
    validate_email,
    validate_password,
    sanitize_input,
    token_required,
)
from extensions import limiter
from sqlalchemy import text

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _get_user_row_dict(row):
    """Helper function to safely convert SQLAlchemy Row to dict"""
    if row is None:
        return None
    return dict(row._mapping) if hasattr(row, "_mapping") else dict(row)


@auth_bp.route("/signup", methods=["POST"])
@limiter.limit("10 per day")
def signup():
    """User registration endpoint"""
    db = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        # Validate and sanitize required fields
        email = sanitize_input(data.get("email", ""))
        password = data.get("password", "")
        full_name = sanitize_input(data.get("full_name", ""))

        if not email or not password or not full_name:
            return (
                jsonify({"error": "Email, password, and full name are required"}),
                400,
            )

        # Validate email
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({"error": message}), 400

        # Database operations
        db = get_db()
        try:
            # Check if user already exists
            result = db.execute(
                text("SELECT id FROM users WHERE email = :email"), {"email": email}
            )
            existing_user = result.fetchone()

            if existing_user:
                return jsonify({"error": "Email already registered"}), 409

            # Hash password
            password_hash = hash_password(password)

            # Generate default profile picture URL
            names = full_name.strip().split()
            if len(names) >= 2:
                initials = f"{names[0][0]}{names[-1][0]}"
            elif names:
                initials = names[0][:2]
            else:
                initials = "SS"

            default_pic = (
                f"https://ui-avatars.com/api/?name={initials}&background=random"
            )

            # Insert new user
            db.execute(
                text(
                    """
                    INSERT INTO users (email, password_hash, full_name, profile_picture)
                    VALUES (:email, :password_hash, :full_name, :profile_picture)
                """
                ),
                {
                    "email": email,
                    "password_hash": password_hash,
                    "full_name": full_name,
                    "profile_picture": default_pic,
                },
            )
            db.commit()

            # Retrieve the created user
            result = db.execute(
                text("SELECT id FROM users WHERE email = :email"), {"email": email}
            )
            user = result.fetchone()
            user_id = _get_user_row_dict(user)["id"] if user else None

            if not user_id:
                return jsonify({"error": "Failed to retrieve user ID"}), 500

            # Generate authentication token
            token = generate_token(user_id, email)

            return (
                jsonify(
                    {
                        "message": "User registered successfully",
                        "token": token,
                        "user": {"id": user_id, "email": email, "full_name": full_name},
                    }
                ),
                201,
            )

        except Exception as e:
            if db:
                db.rollback()
            raise

    except ValueError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500
    finally:
        if db:
            try:
                db.close()
            except:
                pass


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("50 per hour")
def login():
    """User login endpoint"""
    db = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        email = sanitize_input(data.get("email", ""))
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        db = get_db()
        try:
            # Find user by email
            result = db.execute(
                text(
                    """
                    SELECT id, email, password_hash, full_name, bio, profile_picture
                    FROM users WHERE email = :email
                """
                ),
                {"email": email},
            )
            user = result.fetchone()

            if not user:
                return jsonify({"error": "Invalid email or password"}), 401

            # Convert row to dict for consistent access
            user_dict = _get_user_row_dict(user)

            # Verify password
            if not verify_password(password, user_dict["password_hash"]):
                return jsonify({"error": "Invalid email or password"}), 401

            # Generate authentication token
            token = generate_token(user_dict["id"], user_dict["email"])

            return (
                jsonify(
                    {
                        "message": "Login successful",
                        "token": token,
                        "user": {
                            "id": user_dict["id"],
                            "email": user_dict["email"],
                            "full_name": user_dict["full_name"],
                            "bio": user_dict["bio"],
                            "profile_picture": user_dict["profile_picture"],
                        },
                    }
                ),
                200,
            )

        except Exception as e:
            raise

    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500
    finally:
        if db:
            try:
                db.close()
            except:
                pass


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    """Get current user info (requires authentication)"""
    db = None
    try:
        db = get_db()

        result = db.execute(
            text(
                """
                SELECT id, email, full_name, bio, profile_picture, location, availability
                FROM users WHERE id = :user_id
            """
            ),
            {"user_id": current_user["user_id"]},
        )
        user = result.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_dict = _get_user_row_dict(user)

        return (
            jsonify(
                {
                    "user": {
                        "id": user_dict["id"],
                        "email": user_dict["email"],
                        "full_name": user_dict["full_name"],
                        "bio": user_dict["bio"],
                        "profile_picture": user_dict["profile_picture"],
                        "location": user_dict["location"],
                        "availability": user_dict["availability"],
                    }
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Failed to fetch user: {str(e)}"}), 500
    finally:
        if db:
            try:
                db.close()
            except:
                pass
