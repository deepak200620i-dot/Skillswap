from flask import Blueprint, request, jsonify, current_app
from database.db import get_db
from utils import (
    token_required,
    sanitize_input,
    get_profile_picture_url,
    validate_skill_name,
)
from sqlalchemy import text
import os
import uuid
from werkzeug.utils import secure_filename

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


def _allowed_file(filename):
    """Check if file is allowed"""
    ALLOWED_EXTENSIONS = current_app.config.get(
        "ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "gif"}
    )
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@profile_bp.route("/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    """Get user profile by ID"""
    db = None
    try:
        db = get_db()

        # Get user info
        result = db.execute(
            text(
                """
                SELECT id, email, full_name, bio, profile_picture, location, availability, created_at
                FROM users WHERE id = :id
            """
            ),
            {"id": user_id},
        )
        user = result.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_dict = dict(user._mapping)

        # Get user's skills they teach
        result = db.execute(
            text(
                """
            SELECT s.id, s.name, s.category, us.proficiency_level
            FROM skills s
            JOIN user_skills us ON s.id = us.skill_id
            WHERE us.user_id = :user_id AND us.is_teaching = 1
            ORDER BY s.name
        """
            ),
            {"user_id": user_id},
        )
        teaching_skills = [dict(skill._mapping) for skill in result.fetchall()]

        # Get user's skills they want to learn
        result = db.execute(
            text(
                """
            SELECT s.id, s.name, s.category, us.proficiency_level
            FROM skills s
            JOIN user_skills us ON s.id = us.skill_id
            WHERE us.user_id = :user_id AND us.is_learning = 1
            ORDER BY s.name
        """
            ),
            {"user_id": user_id},
        )
        learning_skills = [dict(skill._mapping) for skill in result.fetchall()]

        # Process profile picture URL
        profile_pic = get_profile_picture_url(
            user_dict["profile_picture"], user_dict["full_name"]
        )

        return (
            jsonify(
                {
                    "user": {
                        "id": user_dict["id"],
                        "email": user_dict["email"],
                        "full_name": user_dict["full_name"],
                        "bio": user_dict["bio"],
                        "profile_picture": profile_pic,
                        "location": user_dict["location"],
                        "availability": user_dict["availability"],
                        "created_at": user_dict["created_at"],
                    },
                    "teaching_skills": teaching_skills,
                    "learning_skills": learning_skills,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Failed to fetch profile: {str(e)}"}), 500
    finally:
        if db:
            try:
                db.close()
            except:
                pass


@profile_bp.route("/update", methods=["PUT"])
@token_required
def update_profile(current_user):
    """Update user profile (requires authentication)"""
    db = None
    try:
        user_id = current_user["user_id"]

        # Extract and sanitize fields from JSON or form data
        if request.is_json:
            data = request.get_json() or {}
            full_name = sanitize_input(data.get("full_name"))
            bio = sanitize_input(data.get("bio"))
            location = sanitize_input(data.get("location"))
            availability = sanitize_input(data.get("availability"))
        else:
            full_name = sanitize_input(request.form.get("full_name"))
            bio = sanitize_input(request.form.get("bio"))
            location = sanitize_input(request.form.get("location"))
            availability = sanitize_input(request.form.get("availability"))

        update_fields = []
        params = {"id": user_id}

        # Handle profile picture upload
        if "profile_picture" in request.files:
            file = request.files["profile_picture"]
            if file and file.filename:
                if not _allowed_file(file.filename):
                    return (
                        jsonify(
                            {
                                "error": "File type not allowed. Only PNG, JPG, JPEG, and GIF are allowed"
                            }
                        ),
                        400,
                    )

                try:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"

                    # Create upload directory if it doesn't exist
                    upload_folder = current_app.config.get(
                        "UPLOAD_FOLDER", "static/uploads"
                    )
                    profile_pics_folder = os.path.join(upload_folder, "profile_pics")

                    if not os.path.exists(profile_pics_folder):
                        os.makedirs(profile_pics_folder)

                    # Save file with absolute path
                    file_path = os.path.join(profile_pics_folder, unique_filename)
                    file.save(file_path)

                    # Store relative path in database
                    db_path = f"{profile_pics_folder}/{unique_filename}".replace(
                        "\\", "/"
                    )
                    update_fields.append("profile_picture = :profile_picture")
                    params["profile_picture"] = db_path

                except Exception as file_error:
                    return (
                        jsonify(
                            {
                                "error": f"Failed to save profile picture: {str(file_error)}"
                            }
                        ),
                        500,
                    )

        # Add other fields to update
        if full_name:
            update_fields.append("full_name = :full_name")
            params["full_name"] = full_name

        if bio is not None:
            update_fields.append("bio = :bio")
            params["bio"] = bio

        if location:
            update_fields.append("location = :location")
            params["location"] = location

        if availability:
            update_fields.append("availability = :availability")
            params["availability"] = availability

        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400

        db = get_db()
        try:
            # Update user
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = :id"
            db.execute(text(query), params)
            db.commit()

            # Fetch updated user
            result = db.execute(
                text(
                    """
                    SELECT id, email, full_name, bio, profile_picture, location, availability
                    FROM users WHERE id = :id
                """
                ),
                {"id": user_id},
            )
            updated_user = result.fetchone()

            if not updated_user:
                return jsonify({"error": "User not found after update"}), 404

            updated_dict = dict(updated_user._mapping)

            return (
                jsonify(
                    {
                        "message": "Profile updated successfully",
                        "user": {
                            "id": updated_dict["id"],
                            "email": updated_dict["email"],
                            "full_name": updated_dict["full_name"],
                            "bio": updated_dict["bio"],
                            "profile_picture": get_profile_picture_url(
                                updated_dict["profile_picture"],
                                updated_dict["full_name"],
                            ),
                            "location": updated_dict["location"],
                            "availability": updated_dict["availability"],
                        },
                    }
                ),
                200,
            )

        except Exception as e:
            db.rollback()
            raise

    except Exception as e:
        return jsonify({"error": f"Failed to update profile: {str(e)}"}), 500
    finally:
        if db:
            try:
                db.close()
            except:
                pass


@profile_bp.route("/skills", methods=["POST"])
@token_required
def add_skill(current_user):
    """Add a skill to user's profile"""
    db = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        user_id = current_user["user_id"]

        skill_id = data.get("skill_id")
        proficiency_level = data.get("proficiency_level", "Beginner")
        is_teaching = data.get("is_teaching", False)
        is_learning = data.get("is_learning", False)

        # Validate input
        if not skill_id:
            return jsonify({"error": "skill_id is required"}), 400

        if proficiency_level not in ["Beginner", "Intermediate", "Expert"]:
            return (
                jsonify(
                    {
                        "error": "Invalid proficiency level. Must be Beginner, Intermediate, or Expert"
                    }
                ),
                400,
            )

        if not is_teaching and not is_learning:
            return (
                jsonify({"error": "Must specify is_teaching or is_learning (or both)"}),
                400,
            )

        db = get_db()
        try:
            # Check if skill exists
            result = db.execute(
                text("SELECT id FROM skills WHERE id = :id"), {"id": skill_id}
            )
            skill = result.fetchone()
            if not skill:
                return jsonify({"error": "Skill not found"}), 404

            # Check if user already has this skill
            result = db.execute(
                text(
                    "SELECT id FROM user_skills WHERE user_id = :user_id AND skill_id = :skill_id"
                ),
                {"user_id": user_id, "skill_id": skill_id},
            )
            existing = result.fetchone()

            if existing:
                # Update existing skill
                db.execute(
                    text(
                        """
                    UPDATE user_skills 
                    SET proficiency_level = :level, is_teaching = :teaching, is_learning = :learning
                    WHERE user_id = :user_id AND skill_id = :skill_id
                """
                    ),
                    {
                        "level": proficiency_level,
                        "teaching": is_teaching,
                        "learning": is_learning,
                        "user_id": user_id,
                        "skill_id": skill_id,
                    },
                )
            else:
                # Insert new skill
                db.execute(
                    text(
                        """
                    INSERT INTO user_skills (user_id, skill_id, proficiency_level, is_teaching, is_learning)
                    VALUES (:user_id, :skill_id, :level, :teaching, :learning)
                """
                    ),
                    {
                        "user_id": user_id,
                        "skill_id": skill_id,
                        "level": proficiency_level,
                        "teaching": is_teaching,
                        "learning": is_learning,
                    },
                )

            db.commit()

            return jsonify({"message": "Skill added successfully"}), 201

        except Exception as e:
            db.rollback()
            raise

    except Exception as e:
        return jsonify({"error": f"Failed to add skill: {str(e)}"}), 500
    finally:
        if db:
            try:
                db.close()
            except:
                pass


@profile_bp.route("/skills/<int:skill_id>", methods=["DELETE"])
@token_required
def remove_skill(current_user, skill_id):
    """Remove a skill from user's profile"""
    db = None
    try:
        user_id = current_user["user_id"]

        db = get_db()

        # Verify the skill exists for this user
        result = db.execute(
            text(
                "SELECT id FROM user_skills WHERE user_id = :user_id AND skill_id = :skill_id"
            ),
            {"user_id": user_id, "skill_id": skill_id},
        )
        if not result.fetchone():
            return jsonify({"error": "Skill not found for this user"}), 404

        db.execute(
            text(
                "DELETE FROM user_skills WHERE user_id = :user_id AND skill_id = :skill_id"
            ),
            {"user_id": user_id, "skill_id": skill_id},
        )
        db.commit()

        return jsonify({"message": "Skill removed successfully"}), 200

    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"error": f"Failed to remove skill: {str(e)}"}), 500
    finally:
        if db:
            try:
                db.close()
            except:
                pass
