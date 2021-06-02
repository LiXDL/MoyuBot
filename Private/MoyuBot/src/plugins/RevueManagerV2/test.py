import asyncio
from pathlib import Path

from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, sessionmaker, selectinload, lazyload, with_loader_criteria

from model import Member, Boss, Record, Team


async def test_select_none_exist():
    db_file = Path.cwd().parent.parent.parent.joinpath('Data/Company').joinpath('ORMTest').joinpath('Revue.db')
    aioengien = create_async_engine('sqlite+aiosqlite:///' + str(db_file))

    async_session = sessionmaker(aioengien, class_=AsyncSession)

    async with async_session.begin() as session:
        print(type(session))
        # query_phrase = select(Member).options(selectinload(Member.record)).filter(Member.member_id == '476121826')
        query_phrase = select(Member).options(selectinload(Member.record))
        stream_records = await session.stream(query_phrase)
        print(type(stream_records))
        # exe_records = await session.execute(query_phrase)
        # print(type(exe_records))

        # stream_record = await stream_records.first()
        # print(type(stream_record))
        # print(stream_record.Member.member_id)
        # print(stream_record[0]['id'])
        # exe_record = exe_records.first()

        stream_scalars = stream_records.scalars()
        # exe_scalar = exe_records.scalar()

        # print(type(stream_record))
        # print(type(exe_record))
        print(type(stream_scalars))
        # print(type(exe_scalar))
        # print(exe_scalar.record[0].boss_id)
        #
        # exe_scalars = exe_records.scalars()
        # print(type(exe_scalars))

        stream_members = await stream_records.scalars().all()
        print(stream_members)
        print(type(stream_members[0]))


async def test_fkey():
    db_file = Path.cwd().parent.parent.parent.joinpath('Data/Company').joinpath('ORMTest').joinpath('Revue.db')
    aioengien = create_async_engine('sqlite+aiosqlite:///' + str(db_file), echo=True)
    async_session = sessionmaker(aioengien, class_=AsyncSession)

    async with async_session.begin() as session:
        # stmt = select(Member).options(lazyload(Member.records.and_(Record.date_time >= 1621314000)))
        # query = await session.stream(stmt)
        # records = await query.scalars().all()
        # stmt = select(Record).options(selectinload(Record.member)).filter(Record.member.alias == '潇洒')
        # stmt = select(Member).options(
        #     selectinload(Member.records),
        #     with_loader_criteria(Record, and_(Record.date_time >= 1621314000, Record.date_time <= 1621315000))
        # ).filter(Member.member_id == '476121826')
        stmt = select(Record).options(
            selectinload(Record.member),
            with_loader_criteria(Member, Member.alias == 'fami')
        ).order_by(Record.boss_id)
        query = await session.stream(stmt)
        records = await query.scalars().all()
        member = records[0].member.alias
        print(member)


async def expire_test():
    await test_fkey()


asyncio.run(expire_test())
