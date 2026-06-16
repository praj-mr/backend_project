


from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    name: Optional[str]=None
    email: Optional[str]=None
    role: Optional[str]=None

class LoginRequest(BaseModel):
    email: str
    password: str

class refreshTokenRequest(BaseModel):
    refresh_token: str