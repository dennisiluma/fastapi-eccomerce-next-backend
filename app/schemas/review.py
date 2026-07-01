from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlmodel import Field



class ReviewCreate(BaseModel):

    product_id: int
    rating: int = Field(ge=1, le=5)
    comment: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )


class ReviewResponse(BaseModel):
    
    id: int
    rating: int
    comment: str
    username: str
    created_at: datetime
    product_id: int
    user_id: int

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )
