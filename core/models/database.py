from sqlalchemy.orm import sessionmaker
from cfg import db_str
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

database_url = db_str

engine = create_async_engine(database_url)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session