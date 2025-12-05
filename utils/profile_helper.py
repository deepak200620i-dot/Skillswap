def get_profile_picture_url(profile_picture, full_name):
    """
    Generate profile picture URL with fallback to UI Avatars.
    
    Args:
        profile_picture: The profile_picture value from database
        full_name: User's full name for generating initials
        
    Returns:
        str: URL to profile picture (either uploaded image or UI Avatars)
    """
    # If user has uploaded a custom picture and it's not the old default
    if profile_picture and profile_picture != 'default-avatar.png' and not profile_picture.startswith('https://ui-avatars.com'):
        return profile_picture
    
    # Generate initials for UI Avatars
    names = full_name.strip().split()
    if len(names) >= 2:
        initials = f"{names[0][0]}{names[-1][0]}"
    elif names:
        initials = names[0][:2]
    else:
        initials = "SS"  # Default fallback
    
    return f"https://ui-avatars.com/api/?name={initials}&background=random"
