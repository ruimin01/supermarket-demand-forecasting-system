from flask import Blueprint, request
from services.user_service import get_all_users, update_user_permissions, create_staff_account
from utils.response import success_response, error_response
from utils.auth_helper import user_has_permission

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/users", methods=["POST"])
def users():
    data = request.get_json()
    current_user = data.get("currentUser")

    if not current_user:
        return error_response("current user is required", 401)

    if not user_has_permission(current_user, "can_manage_users"):
        return error_response("no permission to manage users", 403)

    users_data = get_all_users()
    return success_response(users_data)

@user_bp.route("/users/<int:user_id>/permissions", methods=["PUT"])
def update_permissions(user_id):
    data = request.get_json()
    current_user = data.get("currentUser")

    if not current_user:
        return error_response("current user is required", 401)

    if not user_has_permission(current_user, "can_manage_users"):
        return error_response("no permission to manage users", 403)

    permissions = {
        "can_upload": data.get("can_upload", True),
        "can_predict": data.get("can_predict", True),
        "can_export": data.get("can_export", False),
        "can_view_all_records": data.get("can_view_all_records", False),
        "can_view_upload_records": data.get("can_view_upload_records", False),
        "is_active": data.get("is_active", True),
    }

    updated = update_user_permissions(user_id, permissions)

    if updated:
      return success_response(message="permissions updated")

    return error_response("update failed", 400)

@user_bp.route("/users/create", methods=["POST"])
def create_user():
    data = request.get_json()
    current_user = data.get("currentUser")

    if not current_user:
        return error_response("current user is required", 401)

    if not user_has_permission(current_user, "can_manage_users"):
        return error_response("no permission to create staff account", 403)

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    is_active = data.get("is_active", True)

    if not username or not password:
        return error_response("username and password are required", 400)

    result = create_staff_account(username, email, password, is_active)

    if isinstance(result, dict) and result.get("error") == "username already exists":
        return error_response("username already exists", 400)

    return success_response(result, "staff account created")
# from flask import Blueprint, request
# from services.user_service import get_all_users, update_user_permissions
# from utils.response import success_response, error_response
# from utils.auth_helper import user_has_permission

# user_bp = Blueprint("user_bp", __name__)

# @user_bp.route("/users", methods=["POST"])
# def users():
#     data = request.get_json()
#     current_user = data.get("currentUser")

#     if not current_user:
#         return error_response("current user is required", 401)

#     if not user_has_permission(current_user, "can_manage_users"):
#         return error_response("no permission to manage users", 403)

#     data = get_all_users()
#     return success_response(data)

# @user_bp.route("/users/<int:user_id>/permissions", methods=["PUT"])
# def update_permissions(user_id):
#     data = request.get_json()
#     current_user = data.get("currentUser")

#     if not current_user:
#         return error_response("current user is required", 401)

#     if not user_has_permission(current_user, "can_manage_users"):
#         return error_response("no permission to manage users", 403)

#     permissions = {
#         "can_upload": data.get("can_upload", False),
#         "can_predict": data.get("can_predict", True),
#         "can_export": data.get("can_export", False),
#         "can_view_all_records": data.get("can_view_all_records", False),
#         "is_active": data.get("is_active", True),
#     }

#     updated = update_user_permissions(user_id, permissions)

#     if updated:
#         return success_response(message="permissions updated")
#     return error_response("update failed", 400)