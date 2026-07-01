from pathlib import Path
from typing import Optional
from sqlmodel import Session, select
from fastapi import UploadFile, status
from app.models.product import Product
from app.schemas.product import ProductUpdate
from app.core.exceptions import ApiException

from app.services.category import get_category_by_id
from app.services.upload import upload_file, upload_to_s3
from sqlalchemy.orm import selectinload



async def create_product(
    db: Session,
    name: str,
    description: str,
    price: str,
    stock_quantity: int,
    category_id: int,
    file: UploadFile,
):
    
    # first verify to be sure the cateogory id exist
    await get_category_by_id(db, category_id)

    # upload directory
    UPLOAD_DIR = Path("uploads/products")

    # Upload image first
    image_path = await upload_to_s3(file, UPLOAD_DIR)

    db_product = Product(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        category_id=category_id,
        image_url=image_path,
    )

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def get_all_products(db: Session, category_id: Optional[int] = None):
    # 1. Start with the base statement
    statement = select(Product)

    # 2. Add filter if category_id is provided
    if category_id:
        statement = statement.where(Product.category_id == category_id)

    # 3. Execute and return results
    results = await db.exec(statement)
    return results.all()


async def get_product_by_id(db: Session, product_id: int):
    # We use selectinload to eagerly fetch the reviews in one go
    statement = (
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.reviews))
    )

    result = await db.exec(statement)
    product = result.first()

    if not product:
        raise ApiException("Product not found", status.HTTP_404_NOT_FOUND)

    return product


async def update_product(
    db: Session, update_data: ProductUpdate, file: Optional[UploadFile] = None
):

    print("Inside update product")

    db_product = await get_product_by_id(db, update_data.id)

    # Update text fields
    data = update_data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in data.items():
        setattr(db_product, key, value)

    # Update image if new one provided
    if file:
        db_product.image_url = await upload_to_s3(file, Path("uploads/products"))

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product



async def delete_product(db: Session, product_id: int):
    db_product = await get_product_by_id(db, product_id)
    await db.delete(db_product)
    await db.commit()
    return True
