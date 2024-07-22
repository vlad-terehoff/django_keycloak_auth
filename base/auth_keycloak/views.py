from django.shortcuts import redirect
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import exceptions
from .helpers import create_access_token, create_refresh_token, REFRESH_TOKEN_TYPE, KEY_TOKEN, \
    refresh_access_token, ACCESS_TOKEN_TYPE
from .keycloak import get_tokens_from_code, keycloak_openid
from .validation import get_user_or_create, extract_payload_from_token
from django.contrib.auth.models import User


@api_view(["GET"])
@permission_classes([AllowAny])
def keycloak_login(request):
    return redirect(settings.CODE_URL)


@api_view(["GET"])
@permission_classes([AllowAny])
def callback(request):
    code = request.GET["code"]
    token_access_key, token_refresh_key = get_tokens_from_code(code)
    user = get_user_or_create(token=token_access_key)
    access = create_access_token(user)
    refresh_token = create_refresh_token(user)
    resp = Response()
    resp.data = {ACCESS_TOKEN_TYPE: access,
                 "token_type": "Bearer"}
    resp.set_cookie(key=REFRESH_TOKEN_TYPE, value=refresh_token, httponly=True)
    resp.set_cookie(key=KEY_TOKEN, value=token_refresh_key, httponly=True)
    return resp


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):

    refresh_token = request.COOKIES.get(REFRESH_TOKEN_TYPE)
    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided.')
    payload = extract_payload_from_token(refresh_token)

    user = User.objects.filter(id=payload.get('sub')).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('user is inactive')

    access_token = refresh_access_token(user)
    return Response({ACCESS_TOKEN_TYPE: access_token})


@api_view(["GET"])
def keycloak_logout(request):
    resp = Response()
    token_key = request.COOKIES.get(KEY_TOKEN)
    if request.COOKIES.get(REFRESH_TOKEN_TYPE):
        resp.delete_cookie(REFRESH_TOKEN_TYPE)

    if token_key:
        keycloak_openid.logout(token_key)
        resp.delete_cookie(KEY_TOKEN)

    return resp