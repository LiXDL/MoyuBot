import asyncio
import aiosqlite
from pathlib import Path

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

Base = declarative_base()
DB_FILE = Path.cwd().parent.parent.parent.joinpath('Data/Company').joinpath('ORMTest').joinpath('Revue.db')


async def async_main():
    aioengine = create_async_engine('sqlite+aiosqlite:///' + str(DB_FILE), echo=True)

    async with aioengine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(async_main())
