from decimal import Decimal
from typing import List, Optional

from pydantic.alias_generators import to_camel
from pydantic import BaseModel, ConfigDict




class CartItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: Decimal
    product_image: Optional[str]
    quantity: int
    subtotal: Decimal

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )
    

class CartRead(BaseModel):
    id: int
    user_id: int
    items: List[CartItemRead]
    total_quantity: int
    total_price: Decimal

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )





class AddToCartRequest(BaseModel):
    
    product_id: int
    quantity: int = 1

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )
    