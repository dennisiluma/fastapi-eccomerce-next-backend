from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class NotificationType(str, Enum):
    WELCOME = "welcome"
    ORDER_UPDATE = "order_update"
    PAYMENT_UPDATE = "payment_update"
    PROMOTIONAL = "promotional"
    SECURITY = "security"


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Destination email i.e where you wanna send the mail to
    recipient_email: str = Field(index=True)

    # Content of the notification
    title: str = Field()
    message: str = Field()

    notification_type: NotificationType = Field(default=NotificationType.ORDER_UPDATE)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
