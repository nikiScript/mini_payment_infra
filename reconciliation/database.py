from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

DATABASE_URL = os.environ.get("DB_URL_DOCKER")

if DATABASE_URL is None:
    raise ValueError("Missing environment variable: DB_URL_DOCKER")

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
