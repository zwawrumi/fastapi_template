import datetime
from datetime import timedelta
from typing import Optional

from fastapi.security import APIKeyHeader
from jose import jwt
from passlib.context import CryptContext

from config import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_TOKEN

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
apikey_scheme = APIKeyHeader(name='auth')


def hash_password(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, SECRET_TOKEN, algorithm=ALGORITHM)
    return encode_jwt

