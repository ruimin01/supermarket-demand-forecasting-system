from flask import Blueprint, request
from utils.response import success_response, error_response
from utils.auth_helper import user_has_permission
from services.prediction_runtime_service import run_prediction_service

prediction_runtime_bp = Blueprint("prediction_runtime_bp", __name__)

@prediction_runtime_bp.route("/predict-runtime", methods=["POST"])
def predict_runtime():
    data = request.get_json()
    current_user = data.get("currentUser")

    if not current_user:
        return error_response("current user is required", 401)

    if not user_has_permission(current_user, "can_predict"):
        return error_response("no permission to run prediction", 403)

    prediction_category = data.get("predictionCategory")
    stock_code = data.get("stockCode")
    start_date = data.get("startDate")
    end_date = data.get("endDate")

    if not prediction_category or not stock_code or not start_date or not end_date:
        return error_response("predictionCategory, stockCode, startDate and endDate are required", 400)

    try:
        result = run_prediction_service(
            prediction_category=prediction_category,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date
        )
        return success_response(result, "prediction success")
    except Exception as e:
        return error_response(str(e), 500)
# from flask import Blueprint, request
# from utils.response import success_response, error_response
# from utils.auth_helper import user_has_permission
# from services.prediction_runtime_service import run_prediction_service

# prediction_runtime_bp = Blueprint("prediction_runtime_bp", __name__)

# @prediction_runtime_bp.route("/predict", methods=["POST"])
# def predict_runtime():
#     data = request.get_json()
#     current_user = data.get("currentUser")

#     if not current_user:
#         return error_response("current user is required", 401)

#     if not user_has_permission(current_user, "can_predict"):
#         return error_response("no permission to run prediction", 403)

#     prediction_category = data.get("predictionCategory")
#     stock_code = data.get("stockCode")
#     start_date = data.get("startDate")
#     end_date = data.get("endDate")

#     if not prediction_category or not stock_code or not start_date or not end_date:
#         return error_response("predictionCategory, stockCode, startDate and endDate are required", 400)

#     try:
#         result = run_prediction_service(
#             prediction_category=prediction_category,
#             stock_code=stock_code,
#             start_date=start_date,
#             end_date=end_date
#         )
#         return success_response(result, "prediction success")
#     except Exception as e:
#         return error_response(str(e), 500)