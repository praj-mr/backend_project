from app.auth import create_access_tokens, create_refresh_tokens, verify_password
from app.exceptions import InvalidCredentialsException
from app.models.usermodel import User
from app.respositories.user_repository import UserRepository


def login_user(form_data, db):
    get_user = UserRepository.get_user_by_email(db, form_data.username)
    print(get_user.password)
    if not get_user:
        raise Exception("user not found")

    is_valid = verify_password(form_data.password, get_user.password)
    if not is_valid:
        raise InvalidCredentialsException(message="Invalid credentials. Please check your email and password.")

    access_token = create_access_tokens(data={"sub": get_user.email})
    refresh_token = create_refresh_tokens(data={"sub": get_user.email})

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}