

from typing import Optional

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None



class CategoryUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None



class CategoryRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


    #  UPDATE THIS CONFIG
    model_config = ConfigDict(
        from_attributes=True,  # This tells Pydantic to read database object attributes
        exclude_none=True
    )