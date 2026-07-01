from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .category import Category
    from .review import Review
    from .order_item import OrderItem


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    price: Decimal = Field(default=0.0, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(default=0)

    image_url: Optional[str] = Field(default=None)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    # Foreign Key to the Category table
    category_id: int = Field(foreign_key="categories.id")

    # Relationships: one-to-one
    category: "Category" = Relationship(back_populates="products")

    # Relationships  one to many
    order_items: List["OrderItem"] = Relationship(back_populates="product")

    # when a product is deleted, it deletes the reviews under it
    reviews: List["Review"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
