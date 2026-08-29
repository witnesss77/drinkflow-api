from sqlalchemy.pool import NullPool
from core import cfg
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

database_url = cfg.db_str

def create_engine():
    return create_async_engine(
        database_url,
        pool_pre_ping = True
    )

engine = create_engine()
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

celery_engine = create_async_engine(
    database_url,
    poolclass=NullPool,
)

CelerySessionLocal = async_sessionmaker(
    celery_engine,
    expire_on_commit=False
)