

from sqlmodel import Session, select
from fastapi import status
from app.core.exceptions import ApiException
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def create_category(db: Session, category_data: CategoryCreate):
    statement = select(Category).where(Category.name == category_data.name)
    result = await db.exec(statement)

    if result.first():
        raise ApiException("Category already exist", status.HTTP_400_BAD_REQUEST)
    
    db_category = Category(**category_data.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category



async def get_all_categories(db: Session):
    statement = select(Category)
    result = await db.exec(statement)
    return result.all()



async def get_category_by_id(db: Session, category_id: int):
    category = await db.get(Category, category_id)
    if not category:
        raise ApiException("Category not found", status.HTTP_404_NOT_FOUND)
    
    return category



async def update_category(db: Session, update_data: CategoryUpdate):
    db_category = await get_category_by_id(db, update_data.id)
    
    data = update_data.model_dump(exclude_unset=True, exclude_none=True)
    
    for key, value in data.items():
        setattr(db_category, key, value)
  
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category



async def delete_category(db: Session, category_id: int):
    db_category = await get_category_by_id(db, category_id)

    await db.delete(db_category)
    await db.commit()
    return True
