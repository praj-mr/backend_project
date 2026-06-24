import logging

from fastapi import APIRouter, Depends, FastAPI
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal, get_db
from app.exceptions import InvalidCredentialsException
from app.models.usermodel import User
from app.respositories.user_repository import UserRepository
from app.schemas.user_schema import LoginRequest, UserCreate, UserUpdate, refreshTokenRequest
from fastapi import HTTPException
from app.auth import ALGORITHM, SECRET_KEY, admin_required, create_access_tokens, create_refresh_tokens, get_current_user, hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm

from app.services.user_services import login_user


app=FastAPI()
router=APIRouter()
logger = logging.getLogger(__name__)


@router.post("/users")
def create_user(user: UserCreate,db: Session=Depends(get_db)):
    print("password", user.password)
    print("type of password", type(user.password))
    print("lenght of password", len(user.password))
    UserRepository.create_user(db, user)
    
    return {"message": "User created succesfully"}

@router.get('/get_user')
def get_user(curent_user: str = Depends(get_current_user), db: Session=Depends(get_db)):
    users=db.query(User).all()
    return users

@router.get('/users/{user_id}')
def get_user(user_id: int ,db: Session=Depends(get_db)):
    users=db.query(User).filter(User.id==user_id).all()
    if not users:
            raise HTTPException(status_code=404,detail="user not found")
    return users
        


@router.put('/users/{user_id}')
def update_user(user_update: UserUpdate, user_id: int,db: Session=Depends(get_db)):
    try:
        get_user_id=UserRepository.get_user_by_id(db, user_id)
        if user_update.name is not None:
            get_user_id.name=user_update.name
        if user_update.email is not None:
            get_user_id.email=user_update.email

        db.commit()
        db.refresh(get_user_id)
        return {"message": "updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,details="user not found")

@router.delete('/user/{user_id}')
def delete_user(user_id: int, db: Session=Depends(get_db)):
    user=UserRepository.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404,detail="user not found")
    return {"message": "deleted successfully"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm=Depends(),
                db: Session=Depends(get_db)):
    return login_user(form_data, db)
    

@router.get('/me')
def get_me(current_user=Depends(get_current_user)):
    return current_user

@router.get('/admin')
def admin_dashboard(current_user=Depends(admin_required)):
    return {"message": f"welcome to admin dashboard, {current_user.name}"}

@router.post('/refresh')
def refresh_token(request: refreshTokenRequest, db: Session=Depends(get_db)):
    try:
        logger.info("refresh token api called")
        payload=jwt.decode(request.refresh_token,SECRET_KEY,algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401,detail="invalid token")
        
        email=payload.get("sub")
        user=UserRepository.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404,detail="user not found")
        
        access_token=create_access_tokens(data={"sub": user.email})
        refresh_token=create_refresh_tokens(data={"sub": user.email})

        return {"access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401,detail="invalid token")
    
@router.get("/test-error")
async def test_error():
    x=1/0  # This will raise a ZeroDivisionError
    return {"result": x}



