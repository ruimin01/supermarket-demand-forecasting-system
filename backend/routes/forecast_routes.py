from flask import Blueprint, request
from services.forecast_service import run_prediction_service, get_forecast_records
from utils.response import success_response, error_response
from utils.auth_helper import user_has_permission

forecast_bp = Blueprint("forecast_bp", __name__)

@forecast_bp.route("/predict", methods=["POST"])
def predict():
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

    result = run_prediction_service(
        current_user=current_user,
        prediction_category=prediction_category,
        start_date=start_date,
        end_date=end_date,
        stock_code=stock_code
    )

    return success_response(result)

@forecast_bp.route("/forecast-history", methods=["POST"])
def forecast_history():
    data = request.get_json()
    current_user = data.get("currentUser")

    if not current_user:
        return error_response("current user is required", 401)

    result = get_forecast_records(current_user)
    return success_response(result)
# from flask import Blueprint, request
# from services.forecast_service import run_prediction_service, get_forecast_records
# from utils.response import success_response, error_response
# from utils.auth_helper import user_has_permission

# forecast_bp = Blueprint("forecast_bp", __name__)

# @forecast_bp.route("/predict", methods=["POST"])
# def predict():
#     data = request.get_json()

#     # 当前先用前端传来的 currentUser 做演示
#     # 以后正式做法应该是 token/session 解析当前用户
#     current_user = data.get("currentUser")

#     if not current_user:
#         return error_response("current user is required", 401)

#     if not user_has_permission(current_user, "can_predict"):
#         return error_response("no permission to run prediction", 403)

#     product_type = data.get("productType")
#     start_date = data.get("startDate")
#     end_date = data.get("endDate")
#     stock_code = data.get("stockCode")

#     if not product_type or not start_date or not end_date:
#         return error_response("productType, startDate and endDate are required", 400)

#     result = run_prediction_service(current_user, product_type, start_date, end_date, stock_code)
#     return success_response(result)

# @forecast_bp.route("/forecast-history", methods=["POST"])
# def forecast_history():
#     # 这里用 POST 是因为当前前端还没做 token
#     # 你后面接正式鉴权时可以改回 GET + token
#     data = request.get_json()
#     current_user = data.get("currentUser")

#     if not current_user:
#         return error_response("current user is required", 401)

#     result = get_forecast_records(current_user)
#     return success_response(result)