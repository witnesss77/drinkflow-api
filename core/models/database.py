from sqlalchemy.orm import sessionmaker
from core import cfg
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

database_url = cfg.db_str

engine = create_async_engine(url=database_url, pool_pre_ping = True) #poolclass = NullPool на тестах 
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session