from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
pwd_context=CryptContext(schemes=['bcrypt'],
                         deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

SECRET_KEY="my_suoer_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

def create_access_tokens(data: dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt


from fastapi.security import OAuth2PasswordBearer
oauth_scheme=OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        email=payload.get("sub")
        if not email:
            return None
        return email
    except JWTError:
        return None
    
def get_current_user(token: str=Depends(oauth_scheme)):
    email=verify_token(token)
    print(token)
    if not email:
        raise HTTPException(status_code=401,detail="invalid token")
    return email