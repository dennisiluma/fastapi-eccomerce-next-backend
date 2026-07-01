from pydantic import BaseModel, ConfigDict

from pydantic.alias_generators import to_camel

from app.models.notification import NotificationType


class NotificationRead(BaseModel):

    id: int
    recipient_email: str
    title: str
    message: str

    notification_type: NotificationType

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True

    )

