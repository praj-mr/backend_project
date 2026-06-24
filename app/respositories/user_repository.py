from app.models.usermodel import User
from app.schemas.user_schema import UserCreate


class UserRepository:
    @staticmethod
    def get_user_by_email(self, db, email: str):
        return self.db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(self, user: UserCreate):
        new_user = User(
            name=user.name,
            email=user.email,
            password=user.password,
            role=user.role
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
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