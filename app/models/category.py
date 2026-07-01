from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from .product import Product


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None

    # One-to-many relationship
    # when a category id deleted it will delete the products on it
    products: List["Product"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
