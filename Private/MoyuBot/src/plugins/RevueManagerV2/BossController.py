from pathlib import Path

from sqlalchemy import delete, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from .model import Boss
from .constants import DBStatusCode
from .debugger import debugger


#   Use singleton to force single connection.
class BossController(object):
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

    #   Add a new boss record to the BossInfo
    #   The key-value pairs in dict must match the parameter of Boss
    #   i.e. boss_id, alias, health
    @debugger
    async def add(self, info: dict):
        existence = await self._search_single(info['boss_id'], info['alias'])
        if existence:
            return {'result': None, 'code': DBStatusCode.RECORD_ALREADY_EXIST}

        async with self._session.begin() as async_session:
            await async_session.add(Boss(**info))

        #   Nothing is returned for adding
        return{'result': None, 'code': DBStatusCode.INSERT_SUCCESS}

    #   Delete a boss record from the BossInfo
    #   Must only delete by boss_id
    @debugger
    async def delete(self, boss_id: int):
        existence = await self._search_single(boss_id, str(boss_id))
        if not existence:
            return {'result': None, 'code': DBStatusCode.RECORD_NOT_EXIST}

        async with self._session.begin() as async_session:
            stmt = delete(Boss).where(Boss.boss_id == boss_id)
            await async_session.execute(stmt)

        #   Nothing is returned for removing
        return {'result': None, 'code': DBStatusCode.DELETE_SUCCESS}

    #   Update a boss record in the BossInfo
    #   The key-value pairs in dict must match the parameter of Boss
    #   i.e. boss_id, alias, health
    @debugger
    async def update(self, info: dict):
        existence = await self._search_single(info['boss_id'], info['alias'])
        if not existence:
            return {'result': None, 'code': DBStatusCode.RECORD_NOT_EXIST}

        async with self._session.begin() as async_session:
            stmt = update(Boss).where(Boss.boss_id == info['boss_id']).values(**info)
            await async_session.execute(stmt)

        return {'result': None, 'code': DBStatusCode.UPDATE_SUCCESS}

    #   Search a single member record in the CompanyInfo
    @debugger
    async def search(self, identifier: str):
        try:
            boss_id = int(identifier)
            alias = ''
        except ValueError:
            boss_id = 0
            alias = identifier

        record = await self._search_single(boss_id, alias)
        if not record:
            return {'result': {}, 'code': DBStatusCode.SEARCH_SUCCESS}
        else:
            return {'result': {
                'member_id': int(record.boss_id),
                'alias': record.alias,
                'health': int(record.health)
            }, 'code': DBStatusCode.SEARCH_SUCCESS}

    #   List all member records in the CompanyInfo
    @debugger
    async def list(self):
        async with self._session.begin() as async_session:
            query = await async_session.stream(select(Boss))
            records = await query.all()

            result = []
            for record in records:
                result.append({
                    'member_id': int(record.boss_id),
                    'alias': record.alias,
                    'health': int(record.health)
                })
        return {'result': result, 'code': DBStatusCode.SEARCH_SUCCESS}

    #   Helper method for check boss existence
    async def _search_single(self, boss_id: int, alias: str) -> Boss:
        async with self._session.begin() as async_session:
            results = await async_session.stream(
                select(Boss).filter(or_(Boss.boss_id == boss_id, Boss.alias == alias))
            )
            result = await results.first()
        return result
