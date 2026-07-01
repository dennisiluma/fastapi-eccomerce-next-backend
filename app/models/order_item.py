from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .product import Product
    from .order import Order


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(default=1)

    unit_price: Decimal = Field(default=0, max_digits=10, decimal_places=2)

    is_reviewed: bool = Field(default=False)

    # Foreign Keys
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")

    # Relationships
    order: "Order" = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="order_items")
