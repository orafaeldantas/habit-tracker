
from .auth import auth_bp, login_user, logout_user, register_user

# define o que será acessível com "from routes import ..."
__all__ = ["auth_bp", "login_user", "logout_user", "register_user"]