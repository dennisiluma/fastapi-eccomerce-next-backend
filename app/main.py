from contextlib import asynccontextmanager
import re

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import stripe
from app.api.api import api_router
from app.core.exceptions import ApiException, api_exception_handler
from app.db.session import engine
from app.core.config import settings
from sqlmodel import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Attempting to connect to DB")

    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    print("Successfully connected to DB")
    print(f"Successfully connected: {settings.DATABASE_URL}")

    yield


app = FastAPI(title="ShopeEase API", version="0.1.0", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(ApiException, api_exception_handler)


@app.exception_handler(stripe.error.StripeError)
async def stripe_exception_handler(_request: Request, exc: stripe.error.StripeError):
    return JSONResponse(
        status_code=400,
        content={
            "status": 400,
            "message": f"Payment provider Error: {str(exc)}",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "message": "An unexpected eror occured",
            "details": str(exc),
        },
    )


app.include_router(api_router, prefix="/api")
