from uuid import UUID
from passlib.context import CryptContext
from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from dw_blog.models.common import UserType
from dw_blog.config import Settings

settings = Settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
TOKEN_EXPIRATION = settings.TOKEN_EXPIRATION

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_schema = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: UUID,
    user_type: UserType,
):
    encode = {"sub": str(user_id), "user_type": user_type}
    expires = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION)
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(auth_schema)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials!"
    )

    try:
        payload = jwt.decode(
            token=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        user_type = payload.get("user_type")
        if user_id is None or user_type is None:
            raise exception
        auth_user = {"user_id": user_id, "user_type": user_type}
        return auth_user
    except JWTError:
        raise exception


def check_user(
    user_id: str,
    current_user_id: str,
    user_type: UserType
):
    if str(user_id) != str(current_user_id) and user_type != UserType.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can not update other users data!",
        )


def check_if_author(
    user_type: UserType,
):
    return user_type == UserType.author
