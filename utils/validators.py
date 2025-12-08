import re
import html


def validate_email(email):
    """
    Validate email format according to RFC 5322 (simplified)

    Args:
        email (str): Email address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None and len(email) <= 255


def validate_password(password):
    """
    Validate password strength

    Requirements:
    - At least 8 characters (increased from 6)
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character (optional but recommended)

    Args:
        password (str): Password to validate

    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if len(password) > 128:
        return False, "Password must be less than 128 characters"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    return True, "Password is valid"


def sanitize_input(text, max_length=500):
    """
    Sanitize user input by removing whitespace and escaping HTML

    Args:
        text (str): Text to sanitize
        max_length (int): Maximum allowed length (default 500)

    Returns:
        str: Sanitized text or None if input is invalid
    """
    if not text:
        return text

    if not isinstance(text, str):
        return None

    # Strip whitespace
    text = text.strip()

    # Check length
    if len(text) > max_length:
        return None

    # Remove control characters and null bytes
    text = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")

    # Escape HTML special characters
    text = html.escape(text, quote=True)

    return text


def validate_username(username, min_length=3, max_length=32):
    """
    Validate username format

    Args:
        username (str): Username to validate
        min_length (int): Minimum length
        max_length (int): Maximum length

    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not username or len(username) < min_length:
        return False, f"Username must be at least {min_length} characters"

    if len(username) > max_length:
        return False, f"Username must be at most {max_length} characters"

    # Alphanumeric, underscore, hyphen only
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return (
            False,
            "Username can only contain letters, numbers, underscores, and hyphens",
        )

    return True, "Valid username"


def validate_skill_name(name, max_length=100):
    """
    Validate skill name

    Args:
        name (str): Skill name to validate
        max_length (int): Maximum length

    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not name or len(name.strip()) < 2:
        return False, "Skill name must be at least 2 characters"

    if len(name) > max_length:
        return False, f"Skill name must be at most {max_length} characters"

    return True, "Valid skill name"


def validate_rating(rating):
    """
    Validate review rating

    Args:
        rating: Rating value to validate

    Returns:
        tuple: (is_valid: bool, message: str)
    """
    try:
        rating_int = int(rating)
        if 1 <= rating_int <= 5:
            return True, "Valid rating"
        return False, "Rating must be between 1 and 5"
    except (ValueError, TypeError):
        return False, "Rating must be a number between 1 and 5"
