from typing import Any

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review import create_product_review, get_average_rating

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[ReviewResponse]:

    print("inside review API")
    review = await create_product_review(db, current_user, review_in)

    return ApiResponse[ReviewResponse](
        status=status.HTTP_201_CREATED, 
        message="Review Added Successfully", 
        data=review
    )



@router.get("/product/rating/{product_id}", status_code=status.HTTP_200_OK)
async def get_product_rating(
    product_id: int, 
    db: Session = Depends(get_session)
) -> ApiResponse[dict[str, Any]]: 

    rating_data = await get_average_rating(db, product_id)
    
    return ApiResponse[dict[str, Any]](
        status=status.HTTP_200_OK,
        message="Rating fetched successfully",
        data=rating_data
    )