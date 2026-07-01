from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.response import ApiResponse
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenData,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.user import login_user, process_forgot_password, process_reset_password, register_new_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, db: Session = Depends(get_session)
) -> ApiResponse[UserRead]:
    user = await register_new_user(db, user_data)

    return ApiResponse[UserRead](
        status=status.HTTP_201_CREATED,
        message="User Registered Successfully",
        data=user,
    )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    login_data: UserLogin, db: Session = Depends(get_session)
) -> ApiResponse[TokenData]:
    token_info = await login_user(db, login_data)

    return ApiResponse[TokenData](
        status=status.HTTP_200_OK,
        message="Login Successfully",
        data=token_info,
    )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest, db: Session = Depends(get_session)
) -> ApiResponse[None]:
    await process_forgot_password(db, request.email)

    return ApiResponse[None](
        status=status.HTTP_200_OK, message="Reset Password Link Sent Successfully"
    )




@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest, db: Session = Depends(get_session)
) -> ApiResponse[None]:
    await process_reset_password(db, request)

    return ApiResponse[None](
        status=status.HTTP_200_OK,
        message="Password Reset Successfully"
    )