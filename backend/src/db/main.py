from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from src.config import Config
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

# ✅ Use `create_async_engine` for async operations
async_engine = create_async_engine(Config.DATABASE_URL, echo=True, future=True)

# ✅ Create a session factory once, not inside `get_session`
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# ✅ Initialize DB (Only run at startup)
async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# ✅ Correct async session generator
@asynccontextmanager
async def get_db_session():
    session = AsyncSessionLocal()  # ✅ Create session from sessionmaker
    try:
        yield session
    finally:
        await session.close()


async_engine = AsyncEngine(create_engine(url=Config.DATABASE_URL))

async def get_db():
    Session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with Session() as session:
        yield session