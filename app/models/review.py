from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from .user import User
    from .product import Product


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: Optional[int]  = Field(default=None, primary_key=True)
    rating: int = Field(default=5, ge=1, le=5)
    comment: str
    username: str  # <--- This field will store the reviewer's name
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Foreign Keys
    product_id: int = Field(foreign_key="products.id")
    user_id: int = Field(foreign_key="users.id")

    # Back-links
    product: "Product" = Relationship(back_populates="reviews")
    user: "User" = Relationship(back_populates="reviews")

  
