

from decimal import Decimal

from sqlmodel import Session, select
import stripe
from sqlalchemy.orm import selectinload
from fastapi import status
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.core.exceptions import ApiException
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.payment import Payment, PaymentStatus
from app.services.cart import clear_user_cart
from app.services.email import notify_delivery_team_of_order, send_order_confirmation_email, send_payment_notification




async def create_stripe_checkout_session(db: Session, order_id:int):

    # 1. Fetch order with items
    statement = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    result = await db.exec(statement)
    order = result.first()

    if not order:
        raise ApiException("Order not found", 404)
    

    # 2. Prepare line items for Stripe
    line_items = []
    for item in order.items:
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": item.product.name},
                    "unit_amount": int(item.unit_price * 100),  # Stripe uses cents
                },
                "quantity": item.quantity,
            }
        )

    # 3. Create Session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        api_key=settings.STRIPE_SECRET_KEY,
        success_url=f"{settings.PAYMENT_CONFIRMATION_URL}?session_id={{CHECKOUT_SESSION_ID}}",  # The {CHECKOUT_SESSION_ID} is a special dynamic variable provided directly by Stripe,
        cancel_url=f"{settings.PAYMENT_CANCEL_URL}?session_id={{CHECKOUT_SESSION_ID}}",
        metadata={"order_id": str(order.id)},
    )
    return session.url, session.id




async def fullfil_order_payment(db:Session, session_id: str):
    # 1. Retrieve session from Stripe
    try:
        session = stripe.checkout.Session.retrieve(
            session_id, api_key=settings.STRIPE_SECRET_KEY
        )
    except stripe.error.StripeError as e:
        raise ApiException(f"Stripe session error: {str(e)}", 400)

    order_id = int(session.metadata["order_id"])

    # 2. Fetch Order with User relationship
    statement = (
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.user),
            selectinload(Order.payment),
            selectinload(Order.items),
        )
    )
    result = await db.exec(statement)
    order = result.first()

    if not order:
        raise ApiException(f"Order #{order_id} not found in our records.", 404)
    

    # CHECK: Is this order already processed?
    if order.status == OrderStatus.PROCESSING:
        # We return the order gracefully instead of throwing an error,
        # because the user might have just refreshed the page.
        return order

    
    # 3. BRANCHING LOGIC: Check Payment Status
    if session.payment_status == "paid":
        try:
            payment = Payment(
                amount=Decimal(session.amount_total / 100),
                provider_transaction_id=session.payment_intent,
                payment_method="card",
                status=PaymentStatus.COMPLETED,
                order_id=order.id,
            )

            order.status = OrderStatus.PROCESSING

            db.add(payment)
            db.add(order)

            await clear_user_cart(db, order.user_id)
            await db.commit()
            await db.refresh(order)

        except IntegrityError:
            await db.rollback()
            raise ApiException(
                f"Payment for Order #{order.id} has already been recorded.",
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            await db.rollback()
            raise ApiException(f"An unexpected error occurred: {str(e)}", 500)
        

        # ADDED: Confirmed successful order receipt notification
        await send_order_confirmation_email(order.user.email, order.user.name, order)

        # Send Success Email
        await send_payment_notification(
            email=order.user.email,
            name=order.user.name,
            order_id=order.id,
            status="success",
            amount=f"{payment.amount:.2f}",
        )
        # Send Delivery Man Notification Email
        await notify_delivery_team_of_order(
            order, order.user.name
        )  # notify the delivery man to work on the order
        return order

    else:
        # FAILURE PATH
        await send_payment_notification(
            email=order.user.email,
            name=order.user.name,
            order_id=order.id,
            status="failed",
            error="Your card was declined or the transaction was cancelled.",
        )
        # You might want to raise an error here so the frontend knows it failed
        raise ApiException("Payment was not successful. Please try again.", 400)
    




async def cancel_order_payment(db:Session, session_id: str):
    # 1. Retrieve session from Stripe
    try:
        session = stripe.checkout.Session.retrieve(
            session_id, api_key=settings.STRIPE_SECRET_KEY
        )
    except stripe.error.StripeError as e:
        raise ApiException(f"Stripe session error: {str(e)}", 400)

    order_id = int(session.metadata.get("order_id"))

    # 2. Fetch Order with User
    statement = (
        select(Order).where(Order.id == order_id).options(selectinload(Order.user))
    )
    result = await db.exec(statement)
    order = result.first()

    if not order:
        raise ApiException(f"Order #{order_id} not found.", 404)
    

    # 3. Guard Clause: If already paid, don't allow cancellation logic
    if order.status == OrderStatus.PROCESSING:
        return order
    

    # 4. Process Cancellation Logic
    if session.payment_status != "paid":
        try:
            payment_id = session.payment_intent or f"CANCELLED_{session.id}"

            payment = Payment(
                amount=(
                    Decimal(session.amount_total / 100)
                    if session.amount_total
                    else Decimal(0)
                ),
                provider_transaction_id=payment_id,
                payment_method="card",
                status=PaymentStatus.FAILED,
                order_id=order.id,
            )

            # Update order status to CANCELLED
            order.status = OrderStatus.CANCELLED

            db.add(payment)
            db.add(order)

            await db.commit()
            await db.refresh(order)

            # 5. Notify User via Email Service
            await send_payment_notification(
                email=order.user.email,
                name=order.user.full_name,  # Note: used full_name to match your model
                order_id=order.id,
                status="cancelled",
                error="The payment process was cancelled or unsuccessful.",
            )

        except IntegrityError:
            await db.rollback()
            # If we already recorded this failure, just return the order
            return order
        except Exception as e:
            await db.rollback()
            raise ApiException(f"Error during cancellation: {str(e)}", 500)

    return order