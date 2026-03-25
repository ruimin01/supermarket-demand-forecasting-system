from flask import Flask
from flask_cors import CORS

from routes.auth_routes import auth_bp
from routes.product_routes import product_bp
from routes.sales_routes import sales_bp
from routes.forecast_routes import forecast_bp
from routes.upload_routes import upload_bp
from routes.user_routes import user_bp
from routes.test_routes import test_bp
from routes.upload_record_routes import upload_record_bp
from services.model_service import load_model_assets
from routes.prediction_runtime_routes import prediction_runtime_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(product_bp, url_prefix="/api")
    app.register_blueprint(sales_bp, url_prefix="/api")
    app.register_blueprint(forecast_bp, url_prefix="/api")
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(test_bp, url_prefix="/api")
    app.register_blueprint(upload_record_bp, url_prefix="/api")
    app.register_blueprint(prediction_runtime_bp, url_prefix="/api")

    @app.route("/")
    def home():
        return {"message": "Supermarket Demand Prediction Backend Running"}

    return app

app = create_app()

if __name__ == "__main__":
    load_model_assets()
    app.run(host="0.0.0.0", port=5000, debug=True)