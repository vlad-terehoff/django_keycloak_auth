from keycloak import KeycloakOpenID
from django.conf import settings

keycloak_openid = KeycloakOpenID(
    server_url=settings.SERVER_URL,  # https://sso.example.com/auth/
    client_id=settings.CLIENT_ID,  # backend-client-id
    realm_name=settings.REALM,  # example-realm
    client_secret_key=settings.CLIENT_SECRET,  # your backend client secret
    verify=True
)


def get_tokens_from_code(code):
    token = keycloak_openid.token(
        grant_type='authorization_code',
        code=code)

    return token["access_token"], token["refresh_token"]


def get_payload(token: str) -> dict:
    return keycloak_openid.decode_token(token)

