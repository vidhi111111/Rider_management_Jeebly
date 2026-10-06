import os

from flask import Flask, jsonify
from flask_cors import CORS

from .extensions import db, bcrypt
from .routes import register_routes


def create_app() -> Flask:
    app = Flask(__name__)

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:4200"
    )

    database_url = os.getenv(
        "DATABASE_URL",
        "sqlite:///users.db"
    )

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg2://",
            1
        )
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg2://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "1542e59d3455bb7ccdf57c8372e7de9377cc78efb1af36a8532d571e6aac792d"
    )

    allowed_origins = [
        "http://localhost:4200",
        frontend_url
    ]

    CORS(
        app,
        resources={
            r"/*": {
                "origins": allowed_origins
            }
        }
    )

    db.init_app(app)
    bcrypt.init_app(app)
    register_routes(app)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "message": "Bad request."
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "message": "Unauthorized."
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success": False,
            "message": "Forbidden."
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "Resource not found."
        }), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Internal server error."
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred."
        }), 500

    with app.app_context():
        from .models import User, Rider

        db.create_all()

        
    return app