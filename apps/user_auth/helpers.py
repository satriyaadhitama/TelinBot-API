from apps.user_auth.models import User
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError
from utils.jwt import decode_jwt
import jwt


def get_user_from_jwt(tokens):
    jwt_data = decode_jwt(tokens)
    user = User.objects.get(id=jwt_data["user_id"])
    return user


def is_token_expired(token):
    try:
        # Decode the token. Note: This also verifies the token's signature and expiration.
        jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return False  # Token is valid and not expired
    except ExpiredSignatureError:
        return True  # Token is expired
