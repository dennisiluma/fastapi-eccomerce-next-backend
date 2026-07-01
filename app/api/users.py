from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlmodel import Session

from app.api.dependencies import get_current_admin, get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.user import PasswordUpdate, UserRead, UserUpdate
from app.services.user import (
    change_user_password,
    get_all_users_latest,
    update_user_profile,
    upload_profile_pix,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_my_profile(
    currrent_user: User = Depends(get_current_user),
) -> ApiResponse[UserRead]:
    return ApiResponse[UserRead](
        status=status.HTTP_200_OK,
        message="Profile fetched succeessfully",
        data=currrent_user,
    )


@router.get("/all-users", status_code=status.HTTP_200_OK)
async def get_all_users(
    db: Session = Depends(get_session), admin: User = Depends(get_current_admin)
) -> ApiResponse[List[UserRead]]:

    users = await get_all_users_latest(db)

    return ApiResponse[List[UserRead]](
        status=status.HTTP_200_OK, message="All Users fetched succeessfully", data=users
    )


@router.put("/update-profile", status_code=status.HTTP_200_OK)
async def get_my_profile(
    body_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> ApiResponse[UserRead]:

    updated_user = await update_user_profile(db, current_user, body_data)

    return ApiResponse[UserRead](
        status=status.HTTP_200_OK,
        message="Profile updated succeessfully",
        data=updated_user,
    )


@router.put("/change-password", status_code=status.HTTP_200_OK)
async def get_my_profile(
    body_data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> ApiResponse[None]:

    await change_user_password(db, current_user, body_data)

    return ApiResponse[UserRead](
        status=status.HTTP_200_OK, message="Password updated succeessfully"
    )



@router.post("/upload-avatar", status_code=status.HTTP_201_CREATED)
async def upload_profile_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[str]:
    file_path = await upload_profile_pix(db, current_user, file)

    return ApiResponse[str](
        status=status.HTTP_201_CREATED,
        message="Profile Picture Uploded successfully",
        data=file_path,
    )
