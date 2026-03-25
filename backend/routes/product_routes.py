from flask import Blueprint
from services.product_service import get_products
from utils.response import success_response

product_bp = Blueprint("product_bp", __name__)

@product_bp.route("/products", methods=["GET"])
def products():
    data = get_products()
    return success_response(data)