from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.dependencies import get_current_admin
from app.db.session import get_session
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.response import ApiResponse
from app.services.category import (
    create_category,
    delete_category,
    get_all_categories,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["/Categories"])


# PUBLIC ACCESS: Anyone can access this route
@router.get("", status_code=status.HTTP_200_OK)
async def list_categories(
    db: Session = Depends(get_session),
) -> ApiResponse[List[CategoryRead]]:

    categories = await get_all_categories(db)

    return ApiResponse[List[CategoryRead]](
        status=status.HTTP_200_OK,
        message="Categories fetched successfully",
        data=categories,
    )


# ADMIN ONLY ROUTE
@router.post("", status_code=status.HTTP_201_CREATED)
async def add_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
) -> ApiResponse[CategoryRead]:

    created_category = await create_category(db, category_data)

    return ApiResponse[CategoryRead](
        status=status.HTTP_201_CREATED,
        message="Categories created successfully",
        data=created_category,
    )


# ADMIN ONLY ROUTE
@router.put("", status_code=status.HTTP_200_OK)
async def edit_category(
    update_data_to_update: CategoryUpdate,
    db: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
) -> ApiResponse[CategoryRead]:

    updated_category_result = await update_category(db, update_data_to_update)

    return ApiResponse[CategoryRead](
        status=status.HTTP_200_OK,
        message="Categories updated successfully",
        data=updated_category_result,
    )


# ADMIN ONLY ROUTE
@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def remove_category(
    category_id: int,
    db: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
) -> ApiResponse[None]:

    await delete_category(db, category_id)

    return ApiResponse[CategoryRead](
        status=status.HTTP_200_OK, message="Categories Deleted successfully"
    )
