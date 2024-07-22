from .keycloak import get_payload
from django.contrib.auth.models import User
from .utils import decode_jwt
from jwt import InvalidTokenError
from rest_framework import exceptions


def get_user_or_create(token):
    payload = get_payload(token)
    user, created = User.objects.get_or_create(username=payload.get("preferred_username"),
                                               last_name=payload.get('family_name'),
                                               first_name=payload.get('given_name'),
                                               )
    return user


def extract_payload_from_token(token: str) -> dict:
    try:
        payload = decode_jwt(token)
    except InvalidTokenError:
        raise exceptions.AuthenticationFailed('Неверный токен')
    return payload


def get_token_payload(token: str) -> dict:
    return extract_payload_from_token(token)