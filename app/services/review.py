from sqlalchemy import func
from sqlmodel import Session, and_, select
from fastapi import status
from app.core.exceptions import ApiException
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate


async def create_product_review(db: Session, user: User, review_data: ReviewCreate):

    # 1. Eligibility Check
    statement = (
        select(OrderItem)
        .join(Order)
        .where(
            and_(
                Order.user_id == user.id,
                Order.status == OrderStatus.DELIVERED,
                OrderItem.product_id == review_data.product_id,
            )
        )
    )

    result = await db.exec(statement)
    order_item = result.first()

    if not order_item:
        raise ApiException(
            "You can only review products from orders that have been delivered to you.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # 2. Check if user already reviewed this product
    existing_review_stmt = select(Review).where(
        Review.user_id == user.id, Review.product_id == review_data.product_id
    )

    existing_review = (await db.exec(existing_review_stmt)).first()

    if existing_review:
        raise ApiException("You have already reviewed this product.", 400)

    # 3. Create Review
    new_review = Review(
        rating=review_data.rating,
        comment=review_data.comment,
        product_id=review_data.product_id,
        user_id=user.id,
        username=user.name,
    )

    order_item.is_reviewed = True

    db.add(new_review)
    db.add(order_item)

    await db.commit()
    await db.refresh(new_review)
    return new_review



async def get_average_rating(db: Session, product_id: int):
    
    statement = select(
        func.avg(Review.rating).label("average"), 
        func.count(Review.id).label("count")
    ).where(Review.product_id == product_id)

    result = await db.exec(statement)
    stats = result.first()


    # If stats.average is None (no reviews), return 0
    average = round(float(stats.average), 1) if stats and stats.average else 0.0

    total_reviews = stats.count if stats else 0

    return {
        "average_rating": average,
        "total_reviews": total_reviews
    }
