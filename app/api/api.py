from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.category import router as category_router
from app.api.product import router as product_router
from app.api.cart import router as cart_router
from app.api.order import router as order_router
from app.api.review import router as review_router
from app.api.report import router as report_router
from app.api.payment import router as payment_router



api_router = APIRouter()


@api_router.get('/health')
async def health_check():
    return {"message":"API is working"}


api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(category_router)
api_router.include_router(product_router)
api_router.include_router(cart_router)
api_router.include_router(order_router)
api_router.include_router(review_router)
api_router.include_router(report_router)
api_router.include_router(payment_router)