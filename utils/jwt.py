import jwt
from django.conf import settings


def decode_jwt(token):
    try:
        # Decode the token
        # Make sure to use the same secret key and algorithm that were used to create the JWT.
        # Typically, for Django projects using djangorestframework-simplejwt, the secret key is Django's SECRET_KEY.
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        # Handle the case where the token is expired
        return "Token expired"
    except jwt.InvalidTokenError:
        # Handle the case where the token is invalid for any other reason
        return "Invalid token"
