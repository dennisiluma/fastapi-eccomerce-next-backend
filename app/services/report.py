from decimal import Decimal

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.product import Product
from app.models.category import Category
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole


async def get_dashboard_stats(db: Session) -> dict:

    # Get total products
    total_products = (await db.exec(select(func.count()).select_from(Product))).one()
    
    # Get total categories
    total_categories = (await db.exec(select(func.count()).select_from(Category))).one()
    
    # Get total orders
    total_orders = (await db.exec(select(func.count()).select_from(Order))).one()
    
    # Get total users (excluding admins? or all users)
    total_users = (await db.exec(select(func.count()).select_from(User))).one()
    
    total_revenue_stmt = select(func.sum(Order.total_price)).where(
        Order.status.in_([OrderStatus.DELIVERED, OrderStatus.PROCESSING, OrderStatus.SHIPPED])
    )
    total_revenue_result = await db.exec(total_revenue_stmt)

    total_revenue = total_revenue_result.one() or Decimal('0.00')


    
    # Orders by status
    orders_by_status_stmt = select(
        Order.status, 
        func.count(Order.id)
    ).group_by(Order.status)
    orders_by_status_result = await db.exec(orders_by_status_stmt)
    orders_by_status = {status: count for status, count in orders_by_status_result.all()}
    
    # Users by role
    users_by_role_stmt = select(
        User.role, 
        func.count(User.id)
    ).group_by(User.role)
    users_by_role_result = await db.exec(users_by_role_stmt)
    users_by_role = {role: count for role, count in users_by_role_result.all()}
    
    # Low stock products (stock <= 5)
    low_stock_stmt = select(func.count()).select_from(Product).where(Product.stock_quantity <= 5)
    low_stock_result = await db.exec(low_stock_stmt)
    low_stock_products = low_stock_result.one()
    
    # Out of stock products (stock == 0)
    out_of_stock_stmt = select(func.count()).select_from(Product).where(Product.stock_quantity == 0)
    out_of_stock_result = await db.exec(out_of_stock_stmt)
    out_of_stock_products = out_of_stock_result.one()
    
    # Recent orders (last 7 days)
    from datetime import datetime, timedelta
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_orders_stmt = select(func.count()).select_from(Order).where(Order.created_at >= seven_days_ago)
    recent_orders_result = await db.exec(recent_orders_stmt)
    recent_orders = recent_orders_result.one()

    
    return {
        "totalProducts": total_products,
        "totalCategories": total_categories,
        "totalOrders": total_orders,
        "totalUsers": total_users,
        "totalRevenue": float(total_revenue),
        "breakdown": {
            "orders_by_status": {
                "pending": orders_by_status.get(OrderStatus.PENDING, 0),
                "processing": orders_by_status.get(OrderStatus.PROCESSING, 0),
                "shipped": orders_by_status.get(OrderStatus.SHIPPED, 0),
                "delivered": orders_by_status.get(OrderStatus.DELIVERED, 0),
                "cancelled": orders_by_status.get(OrderStatus.CANCELLED, 0),
            },
            "users_by_role": {
                "admin": users_by_role.get(UserRole.ADMIN, 0),
                "customer": users_by_role.get(UserRole.CUSTOMER, 0),
                "delivery": users_by_role.get(UserRole.DELIVERY, 0),
            },
            "inventory_status": {
                "low_stock_products": low_stock_products,
                "out_of_stock_products": out_of_stock_products,
            },
            "recent_orders_last_7_days": recent_orders,
        }
    }

    
