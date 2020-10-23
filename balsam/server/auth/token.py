from datetime import datetime
from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError

from balsam.server import settings
from balsam import schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def create_access_token(user):

    expiry = datetime.utcnow() + settings.auth.token_ttl
    to_encode = {"sub": user.id, "exp": expiry, "username": user.username}
    encoded_jwt = jwt.encode(
        to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm
    )
    return encoded_jwt, expiry


def user_from_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_token_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Expired Token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.auth.secret_key, algorithms=[settings.auth.algorithm],
        )

        user_id: int = payload["sub"]
        username: str = payload["username"]
        expiry = payload["exp"]

        utc_now = (datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds()
        if expiry <= utc_now:
            raise expired_token_exc

        if user_id is None or username is None:
            raise credentials_exception

    except PyJWTError:
        raise credentials_exception

    return schemas.UserOut(id=user_id, username=username)