from flask import Flask, jsonify
from flask_cors import CORS
from .extensions import db, bcrypt
from .routes import register_routes


def create_app() -> Flask:
    app = Flask(__name__)

    CORS(
        app,
        resources={r"/*": {"origins": "http://localhost:4200"}}
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "1542e59d3455bb7ccdf57c8372e7de9377cc78efb1af36a8532d571e6aac792d"

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
        from .models import User
        db.create_all()

    return app