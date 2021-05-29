from pathlib import Path

from sqlalchemy import delete, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from .model import Member
from .constants import DBStatusCode
from .debugger import debugger


#   Use singleton to force single connection.
class MemberController(object):
    __instance = None

    def __new__(cls, db_path: Path):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__engine = create_async_engine('sqlite+aiosqlite:///' + str(db_path))
            cls._session = sessionmaker(cls.__engine, expire_on_commit=False, class_=AsyncSession)
        return cls.__instance

    def __init__(self, db_path: Path):
        pass

    @classmethod
    def change_database(cls, db_path: Path):
        cls.__engine = create_async_engine('sqlite+aiosqlite:///' + str(db_path))
        cls._session = sessionmaker(cls.__engine, expire_on_commit=False, class_=AsyncSession)

    #   Add a new member record to the CompanyInfo
    #   The key-value pairs in dict must match the parameter of Member
    #   i.e. member_id, alias, account, password
    @debugger
    async def add(self, info: dict):
        existence = await self._search_single(info['member_id'], info['alias'])
        if existence:
            return {'result': None, 'code': DBStatusCode.RECORD_ALREADY_EXIST}

        async with self._session.begin() as async_session:
            await async_session.add(Member(**info))

        #   Nothing is returned for adding
        return {'result': None, 'code': DBStatusCode.INSERT_SUCCESS}

    #   Delete a member record from the CompanyInfo
    #   Must only delete by member_id
    @debugger
    async def delete(self, member_id: str):
        existence = await self._search_single(member_id, member_id)
        if not existence:
            return {'result': None, 'code': DBStatusCode.RECORD_NOT_EXIST}

        async with self._session.begin() as async_session:
            stmt = delete(Member).where(Member.member_id == member_id)
            await async_session.execute(stmt)

        #   Nothing is returned for removing
        return {'result': None, 'code': DBStatusCode.DELETE_SUCCESS}

    #   Update a member record in the CompanyInfo
    #   The key-value pairs in dict must match the parameter of Member
    #   i.e. member_id, alias, account, password
    @debugger
    async def update(self, info: dict):
        existence = await self._search_single(info['member_id'], info['alias'])
        if not existence:
            return {'result': None, 'code': DBStatusCode.RECORD_NOT_EXIST}

        async with self._session.begin() as async_session:
            stmt = update(Member).where(Member.member_id == info['member_id']).values(**info)
            await async_session.execute(stmt)

        return {'result': None, 'code': DBStatusCode.UPDATE_SUCCESS}

    #   Search a single member record in the CompanyInfo
    @debugger
    async def search(self, identifier: str):
        record = await self._search_single(identifier, identifier)
        if not record:
            return {'result': {}, 'code': DBStatusCode.SEARCH_SUCCESS}
        else:
            return {'result': {
                'member_id': record.member_id,
                'alias': record.alias,
                'account': record.account,
                'password': record.password
            }, 'code': DBStatusCode.SEARCH_SUCCESS}

    #   List all member records in the CompanyInfo
    @debugger
    async def list(self):
        async with self._session.begin() as async_session:
            query = await async_session.stream(select(Member))
            records = await query.all()

            result = []
            for record in records:
                result.append({
                    'member_id': record.member_id,
                    'alias': record.alias,
                    'account': record.account,
                    'password': record.password
                })
        return {'result': result, 'code': DBStatusCode.SEARCH_SUCCESS}

    #   Helper method for check member existence
    async def _search_single(self, member_id: str, alias: str) -> Member:
        async with self._session.begin() as async_session:
            results = await async_session.stream(
                select(Member).filter(or_(Member.member_id == member_id, Member.alias == alias))
            )
            result = await results.first()
        return result
