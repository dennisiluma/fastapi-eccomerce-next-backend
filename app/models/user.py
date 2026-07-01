from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel



if TYPE_CHECKING:
    from .order import Order
    from .review import Review
    from .cart import Cart



class UserRole(str, Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    DELIVERY = "DELIVERY"



class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    email: str = Field(index=True, unique=True)
    hashed_password: str = Field()
    name: str = Field(index=True)
    profile_picture: Optional[str] = None
    address: Optional[str] = None

    role: UserRole = Field(default=UserRole.CUSTOMER, index=True)

    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # One-to-many relationship
    orders: List["Order"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")
    
    # one-to-one relationship
    cart: Optional["Cart"] = Relationship(back_populates="user")

