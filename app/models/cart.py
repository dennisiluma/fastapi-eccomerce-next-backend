from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from .product import Product
    from .user import User


class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id", unique=True)

    # Relationships
    user: "User" = Relationship(back_populates="cart")
    items: List["CartItem"] = Relationship(back_populates="cart")


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"
    id: Optional[int] = Field(default=None, primary_key=True)

    # 4. Foreign Keys
    cart_id: int = Field(foreign_key="carts.id")
    product_id: int = Field(foreign_key="products.id")

    quantity: int = Field(default=1)

    # Relationships
    cart: "Cart" = Relationship(back_populates="items")
    product: "Product" = Relationship()
