from flask import Blueprint, request
from services.upload_record_service import get_upload_records
from utils.response import success_response, error_response
from utils.auth_helper import user_has_permission

upload_record_bp = Blueprint("upload_record_bp", __name__)

@upload_record_bp.route("/upload-records", methods=["POST"])
def upload_records():
    data = request.get_json()
    current_user = data.get("currentUser")

    if not current_user:
        return error_response("current user is required", 401)

    if not user_has_permission(current_user, "can_view_upload_records"):
        return error_response("no permission to view upload records", 403)

    records = get_upload_records()
    return success_response(records)