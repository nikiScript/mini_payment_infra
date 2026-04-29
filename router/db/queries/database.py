from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
DATABASE_URL_DOCKER = os.environ.get("DB_URL_DOCKER")
print(DATABASE_URL_DOCKER)

if DATABASE_URL_DOCKER is None:
    raise ValueError("Missing environment variable: DB_URL")

engine = create_async_engine(DATABASE_URL_DOCKER)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session