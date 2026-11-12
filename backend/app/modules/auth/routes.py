from flask import Blueprint
from .controllers import AuthController

auth_bp = Blueprint("auth", __name__)
controller = AuthController()


@auth_bp.get("/health")
def health():
    return controller.health()


@auth_bp.post("/register")
def register():
    return controller.register()


@auth_bp.post("/login")
def login():
    return controller.login()
