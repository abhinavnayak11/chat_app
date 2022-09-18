from passlib.context import CryptContext
from jose import jwt

from . import db

APP_SECRET_KEY = "VEGA_SECRET"
crypt_context = CryptContext(schemes=["bcrypt"])


def get_jwt_token_from_number(number: str) -> str:
    return jwt.encode({"number": number}, APP_SECRET_KEY)

def get_user_from_jwt_token(token: str) -> db.User:
    try:
        return db.get_user(jwt.decode(token, APP_SECRET_KEY)["number"])
    except Exception as e:
        print(e)
        return db.EMPTY_USER