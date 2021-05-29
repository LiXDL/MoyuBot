import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, sessionmaker, selectinload

from model import Member, Boss, Record, Team


async def test_select_none_exist():
    db_file = Path.cwd().parent.parent.parent.joinpath('Data/Company').joinpath('ORMTest').joinpath('Revue.db')
    aioengien = create_async_engine('sqlite+aiosqlite:///' + str(db_file))

    async_session = sessionmaker(aioengien, class_=AsyncSession)

    async with async_session() as session:
        query_phrase = select(Member).options(selectinload(Member.record)).filter(Member.member_id == '843658')

        test_records = await session.stream(query_phrase)
        empty_record = await test_records.first()
        print(empty_record)

    return empty_record


async def expire_test():
    result = await test_select_none_exist()
    print('outside')
    print(result[0])


asyncio.run(expire_test())
