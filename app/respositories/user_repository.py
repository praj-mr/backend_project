from app.auth import hash_password
from app.models.usermodel import User
from app.schemas.user_schema import UserCreate


class UserRepository:
    @staticmethod
    def get_user_by_email(db, email: str):
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db, user: UserCreate):
        hased_password = hash_password(user.password)
        new_user = User(
            name=user.name,
            email=user.email,
            password=hased_password,
            role=user.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    def get_user_by_id(self, db, user_id: int):
        return db.query(User).filter(User.id == user_id).first()
    
    def delete_user(self, db, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False