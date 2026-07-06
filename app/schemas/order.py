from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic.alias_generators import to_camel

from pydantic import BaseModel, ConfigDict, computed_field, model_validator
from sqlmodel import Field

from app.models.order import OrderStatus



class CheckoutRequest(BaseModel):
    shipping_address: str

class OrderStatusUpdate(BaseModel):
    status: OrderStatus




class OrderItemRead(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = Field(default=None, alias="productName")
    quantity: int
    unit_price: Decimal
    is_reviewed: bool
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

    @model_validator(mode='before')
    @classmethod
    def map_fields_from_relationships(cls, data):
        if hasattr(data, "product"):
            return {
                "id": data.id,
                "product_id": data.product_id,
                "product_name": data.product.name if data.product else "Unknown",
                "quantity": data.quantity,
                "unit_price": data.unit_price,
                "is_reviewed": data.is_reviewed,
            }
        return data

    @computed_field
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price


class OrderRead(BaseModel):
    id: int
    user_id: int
    total_price: Decimal
    status: OrderStatus
    shipping_address: str
    created_at: datetime
    items: List[OrderItemRead] = []
    
    

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )




    
    
    
    