from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.cart import AddToCartRequest, CartRead
from app.schemas.response import ApiResponse
from app.services.cart import (
    add_item_to_cart,
    clear_user_cart,
    decrement_item_quantity,
    get_user_cart,
    remove_item_from_cart,
)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", status_code=status.HTTP_200_OK)
async def view_cart(
    db: Session = Depends(get_session), user: User = Depends(get_current_user)
) -> ApiResponse[CartRead]:

    cart = await get_user_cart(db, user.id)

    return ApiResponse[CartRead](
        status=status.HTTP_200_OK, message="Cart retrieved", data=cart
    )


@router.post("/add", status_code=status.HTTP_200_OK)
async def add_to_cart(
    req: AddToCartRequest,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:

    await add_item_to_cart(db, user.id, req.product_id, req.quantity)

    return ApiResponse[None](
        status=status.HTTP_200_OK, message="Item added to cart"
    )


@router.post("/decrement/{product_id}", status_code=status.HTTP_200_OK)
async def decrement_cart_item(
    product_id: int,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    await decrement_item_quantity(db, user.id, product_id)

    return ApiResponse[None](
        status=status.HTTP_200_OK, message="Item decremented successfully"
    )


@router.delete("/remove/{product_id}", status_code=status.HTTP_200_OK)
async def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    await remove_item_from_cart(db, user.id, product_id)

    return ApiResponse[None](
        status=status.HTTP_200_OK, message="Item removed"
    )


@router.delete("/clear", status_code=status.HTTP_200_OK)
async def clear_cart(
    db: Session = Depends(get_session), user: User = Depends(get_current_user)
) -> ApiResponse[None]:
    await clear_user_cart(db, user.id)

    return ApiResponse[None](status=status.HTTP_200_OK, message="Cart cleared")
