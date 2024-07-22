from django.conf import settings
from datetime import timedelta
from .utils import encode_jwt
from django.contrib.auth.models import User


TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
KEY_TOKEN = "key_refresh"


def create_jwt(token_type: str,
               token_data: dict,
               expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
               expire_timedelta: timedelta | None = None) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(payload=jwt_payload,
                      expire_minutes=expire_minutes,
                      expire_timedelta=expire_timedelta)


def create_access_token(user: User, time: int | None = None):
    jwt_payload = {
        "sub": user.pk,
        "username": user.username
    }

    if time:
        expire_minutes = time

    else:
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    return create_jwt(token_type=ACCESS_TOKEN_TYPE,
                            token_data=jwt_payload,
                            expire_minutes=expire_minutes)


def create_refresh_token(user: User):
    jwt_payload = {
        "sub": user.pk
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))


def refresh_access_token(user: User):
    jwt_payload = {
        "sub": user.pk,
        "username": user.username
    }
    return create_jwt(token_type=ACCESS_TOKEN_TYPE,
                            token_data=jwt_payload,
                            expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def refresh_token_refresh(user: dict):
    jwt_payload = {
        "sub": user.get("sub")
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
