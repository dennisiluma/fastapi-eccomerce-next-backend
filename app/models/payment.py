from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel



if TYPE_CHECKING:
    from .order import Order


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"




class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    id: Optional[int]  = Field(default=None, primary_key=True)
    
    amount: Decimal = Field(default=0.0, max_digits=10, decimal_places=2)
    currency: str = Field(default="usd")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    
    # Stripe or PayPal Transaction ID
    provider_transaction_id: str = Field(index=True, unique=True) 
    payment_method: str  # e.g., "card", "bank_transfer"
    
    # Relationships
    order_id: int = Field(foreign_key="orders.id", unique=True)
    order: "Order" = Relationship(back_populates="payment")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


