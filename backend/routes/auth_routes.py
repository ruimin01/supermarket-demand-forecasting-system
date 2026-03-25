from flask import Blueprint, request
from services.auth_service import login_user
from utils.response import success_response, error_response

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = login_user(username, password)

    if not user:
        return error_response("invalid username or password", 401)

    if isinstance(user, dict) and user.get("error") == "account disabled":
        return error_response("account disabled", 403)

    return success_response(user, "login success")