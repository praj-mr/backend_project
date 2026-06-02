from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.usermodel import User
from app.schemas.user_schema import LoginRequest, UserCreate, UserUpdate
from fastapi import HTTPException
from app.auth import create_access_tokens, get_current_user, hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm


app=FastAPI()
router=APIRouter()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users")
def create_user(user: UserCreate,db: Session=Depends(get_db)):
    new_user=User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
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
        get_user_id=db.query(User).filter(User.id==user_id).first()
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
    user=db.query(User).filter(User.id==user_id).delete()
    if not user:
        raise HTTPException(status_code=404,detail="user not found")
    db.commit()
    return {"message": "deleted successfully"}

@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm=Depends(),
                db: Session=Depends(get_db)):
    get_user=db.query(User).filter(User.email==form_data.username).first()

    if not get_user:
        raise HTTPException(status_code=404,detail="user not found")
    
    is_valid=verify_password(form_data.password, get_user.password)
    if not is_valid:
        raise HTTPException(status_code=401,detail="invalid email or password")
    
    access_token=create_access_tokens(data={"sub": get_user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get('/me')
def get_me(current_user=Depends(get_current_user)):
    return current_user

