from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///./url_maps.db'
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(expire_on_commit=False, bind=async_engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_async_db():
    async with AsyncSessionLocal() as session:
       yield session

async def async_create_db_tables():
    async with async_engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)

DB_SESSION = Annotated[AsyncSession, Depends(get_async_db)]