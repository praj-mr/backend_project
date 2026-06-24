import logging

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.usermodel import User
pwd_context=CryptContext(schemes=['bcrypt'],
                         deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

SECRET_KEY="my_suoer_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

def create_access_tokens(data: dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt

def create_refresh_tokens(data: dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt


from fastapi.security import OAuth2PasswordBearer
oauth_scheme=OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str, db: Session=Depends(get_db)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        email=payload.get("sub")
        user=db.query(User).filter(User.email==email).first()
        if not user:
            return None
        return user
    except JWTError:
        return None
    
def get_current_user(token: str=Depends(oauth_scheme), db: Session=Depends(get_db)):
    user=verify_token(token, db)
    print(token)
    if not user:
        raise HTTPException(status_code=401,detail="invalid token")
    return user

def admin_required(current_user: User=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403,detail="admin access required")
    return current_user

