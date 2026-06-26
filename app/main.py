import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database.connection import engine, Base
from app.models.usermodel import User
from app.routers.user_router import router
from app.exceptions import InvalidCredentialsException

app=FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(router)

@app.get("/")
def home():
    return{"message": 'first backend project started successfully'}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request: {request.method} {request.url.path} completed in {process_time:.4f} seconds")
    print(f"Response status code: {response.status_code}")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"An error occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred. Please try again later.",
                  "error": str(exc)},
    )

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_exception_handler(request: Request, exc: InvalidCredentialsException):
    logging.error(f"Invalid credentials: {exc.message}")
    return JSONResponse(
        status_code=401,
        content={"message": exc.message},
    )