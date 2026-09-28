from flask import Flask
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

    with app.app_context(): 
        from .models import User
        db.create_all()

    return app