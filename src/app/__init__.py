from flask import Flask
from .routes import image_bp, debug_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(image_bp)
    app.register_blueprint(debug_bp, url_prefix="/debug")

    return app

