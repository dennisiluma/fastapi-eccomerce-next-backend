


from fastapi import APIRouter,status,Depends
from typing import Any

from sqlmodel import Session
from app.db.session import get_session
from app.schemas.response import ApiResponse
from app.services.payment import fullfil_order_payment, cancel_order_payment


router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/confirm", status_code=status.HTTP_200_OK)
async def confirm_payment(
    session_id: str, 
    db: Session = Depends(get_session)
) -> ApiResponse[Any]:
    
    order = await fullfil_order_payment(db, session_id)

    return ApiResponse[Any](
        status=status.HTTP_200_OK, 
        message="Payment verified and order is now being processed.", 
        data=order
    )


@router.get("/cancel", status_code=status.HTTP_200_OK)
async def cancel_payment(
    session_id: str, 
    db: Session = Depends(get_session)
) -> ApiResponse[dict[str, int]]:
    order = await cancel_order_payment(db, session_id)
    
    return ApiResponse[dict[str, int]](
        status=status.HTTP_200_OK, 
        message="Payment was cancelled. You can try paying again from your order history.", 
        data={"order_id": order.id}
    )
