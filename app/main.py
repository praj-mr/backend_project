from fastapi import FastAPI

from app.database.connection import engine, Base
from app.models.usermodel import User
from app.routers.user_router import router

app=FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(router)

@app.get("/")
def home():
    return{"message": 'first backend project started successfully'}