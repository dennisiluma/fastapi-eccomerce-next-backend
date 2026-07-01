from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict


T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):

    status: int
    message: str
    data: T | None = None


    model_config = ConfigDict(
        from_attributes=True,
        exclude_none = True
    )