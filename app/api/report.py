from typing import Any

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.dependencies import get_current_admin
from app.db.session import get_session
from app.models.user import User
from app.schemas.response import ApiResponse
from app.services.report import get_dashboard_stats

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard", status_code=status.HTTP_200_OK)
async def get_dashboard_report(
    db: Session = Depends(get_session), admin: User = Depends(get_current_admin)
) -> ApiResponse[dict[str, Any]]:

    stats = await get_dashboard_stats(db)

    return ApiResponse[dict[str, Any]](
        status=status.HTTP_200_OK,
        message="Dashboard statistics retrieved successfully",
        data=stats,
    )
