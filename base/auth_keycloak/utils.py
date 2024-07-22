from datetime import datetime, timedelta, timezone
from django.conf import settings
import jwt


def encode_jwt(
        payload: dict,
        private_key: str = settings.PRIVATE_KEY_PATH.read_text(),
        algorithm: str = settings.ALGORITHM,
        expire_timedelta: timedelta | None = None,
        expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES

):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        iat=now,
        exp=expire
    )
    encode = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm
    )
    return encode


def decode_jwt(
        token: str | bytes,
        public_key: str = settings.PUBLIC_KEY_PATH.read_text(),
        algorithm: str = settings.ALGORITHM
):
    decode = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )

    return decode
