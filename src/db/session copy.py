# futurisys-ml-deploy/src/db/session.py

import os
from typing import AsyncGenerator

from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (  # fmt: off; fmt: on
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# 🔧 Suppression des query params (sslmode, etc.)
url = make_url(DATABASE_URL).set(query={})

engine = create_async_engine(
    url,
    echo=False,
    connect_args={"ssl": "require"},  # ✅ compatible asyncpg + Neon
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
