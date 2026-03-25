from flask import Blueprint, request
from services.sales_service import get_sales_history
from utils.response import success_response

sales_bp = Blueprint("sales_bp", __name__)

@sales_bp.route("/sales-history", methods=["GET"])
def sales_history():
    stock_code = request.args.get("stock_code")
    data = get_sales_history(stock_code)
    return success_response(data)