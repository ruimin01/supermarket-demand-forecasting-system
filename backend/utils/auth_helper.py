def user_has_permission(user, permission_key):
    permissions = user.get("permissions", {})
    return bool(permissions.get(permission_key, False))