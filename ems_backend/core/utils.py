def get_user_role(user):
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return "SuperAdmin"
    if hasattr(user, "role") and user.role:
        return user.role.name
    return None
