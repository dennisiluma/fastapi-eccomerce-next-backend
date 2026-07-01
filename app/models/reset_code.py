from datetime import datetime, timedelta, timezone
from typing import  Optional
from sqlmodel import Field, SQLModel



class ResetCode(SQLModel, table=True):
    __tablename__ = "reset_codes"

    id: Optional[int] = Field(default=None, primary_key=True)

    email: str = Field(index=True)
    code: str = Field(unique=True, index=True)

    # Valid for 5 hours as per our requirement
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)+ timedelta(hours=5)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
