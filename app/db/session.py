
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=False)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        yield session