from flask import jsonify

def success_response(data=None, message="success", status=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status

def error_response(message="error", status=400):
    return jsonify({
        "success": False,
        "message": message
    }), status