from typing import Any, List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.dependencies import get_current_admin_or_delivery, get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.order import OrderRead, OrderStatusUpdate
from app.schemas.response import ApiResponse
from app.services.order import get_all_order, get_orders_of_user, process_checkout, update_order_status

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
async def checkout(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
) -> ApiResponse[dict[str, Any]]:
    result = await process_checkout(db, current_user)

    order = result["order"]
    checkout_url = result["checkout_url"]
    session_id = result["session_id"]

    return ApiResponse[dict[str, Any]](
        status=status.HTTP_201_CREATED,
        message="Order placed.  Redirecting to payment...",
        data={
            "id": order.id,
            "checkoutUrl": checkout_url,
            "session_id": session_id,
            "total_price": order.total_price
        }
    )


@router.get("/me", status_code=status.HTTP_200_OK)
async def my_orders(
    db: Session = Depends(get_session), user: User = Depends(get_current_user)
) -> ApiResponse[List[OrderRead]]:
    orders = await get_orders_of_user(db, user.id)

    return ApiResponse[List[OrderRead]](
        status=status.HTTP_200_OK, message="Orders fetched", data=orders
    )



@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_orders_endpoint(
    db: Session = Depends(get_session),
    user: User = Depends(get_current_admin_or_delivery),
) -> ApiResponse[List[OrderRead]]:

    orders = await get_all_order(db)

    return ApiResponse[List[OrderRead]](
        status=status.HTTP_200_OK,
        message="All orders fetched successfully",
        data=orders,
    )




@router.patch("/{order_id}/status", status_code=status.HTTP_200_OK)
async def admin_update_status(
    order_id: int, 
    status_data: OrderStatusUpdate, 
    db: Session = Depends(get_session), 
    user: User = Depends(get_current_admin_or_delivery)
) -> ApiResponse[OrderRead]:
    order = await update_order_status(db, order_id, status_data)
    
    return ApiResponse[OrderRead](
        status=status.HTTP_200_OK, 
        message=f"Order marked as {status_data.status}", 
        data=order
    )