from ..modules.auth.services import AuthService

_auth_service = AuthService()


def authenticate_user(email, password):
    success, _, data, _ = _auth_service.login(email, password)
    return data if success else None
