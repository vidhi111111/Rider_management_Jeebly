
import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv

from .extensions import db, bcrypt
from .routes import register_routes


def create_app() -> Flask:

    load_dotenv()

    app = Flask(__name__)

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:4200"
    )
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. Configure it in the "
            "local .env file or Render Environment Variables."
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

    # Secret key configuration
    secret_key = os.getenv("SECRET_KEY")

    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY is missing. Configure it in the "
            "local .env file or Render Environment Variables."
        )

    app.config["SECRET_KEY"] = secret_key

    # CORS configuration for local and deployed frontend
    allowed_origins = list({
        "http://localhost:4200",
        frontend_url
    })

    CORS(
        app,
        resources={
            r"/*": {
                "origins": allowed_origins
            }
        }
    )

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)

    # Register API routes
    register_routes(app)

    # Error handlers
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
        app.logger.exception("Internal server error")

        return jsonify({
            "success": False,
            "message": "Internal server error."
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback()
        app.logger.exception("Unhandled application error")

        return jsonify({
            "success": False,
            "message": "An unexpected error occurred."
        }), 500

    from .models import User, Rider, Order

    return app
