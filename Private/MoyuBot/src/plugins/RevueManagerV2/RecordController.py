from sqlalchemy import delete, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, selectinload, with_loader_criteria

from .model import Member, Boss, Record
from .constants import DBStatusCode
from .debugger import debugger


#   Use singleton to force single connection.
class RecordController(object):
    __instance = None

    def __new__(cls, db_path: str):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__engine = create_async_engine('sqlite+aiosqlite:///' + db_path)
            cls.__session = sessionmaker(cls.__engine, expire_on_commit=False, class_=AsyncSession)
        return cls.__instance

    def __init__(self, db_path: str):
        pass

    @classmethod
    def change_database(cls, db_path: str):
        cls.__engine = create_async_engine('sqlite+aiosqlite:///' + str(db_path))
        cls.__session = sessionmaker(cls.__engine, expire_on_commit=False, class_=AsyncSession)

    #   Add a new revue record to the RevueRecord
    #   The key-value pairs in dict must match the parameter of Record
    #   i.e. member_id, boss_id, damage, sequence, turn, team, date_time
    @debugger
    async def add(self, info: dict):
        async with self.__session.begin() as async_session:
            await async_session.add(Record(**info))

        #   Nothing is returned for adding
        return{'result': None, 'code': DBStatusCode.INSERT_SUCCESS}

    #   Delete a revue record from the RevueRecord
    #   Deletion is performed based on member_id/alias, boss_id/alias, and damage
    @debugger
    async def delete(self, member_identifier: str, boss_identifier: str, damage: int):
        member_id = await self._member_id_locator(member_identifier)
        boss_id = await self._boss_id_locator(boss_identifier)

        if member_id == '' or boss_id == -1:
            return {'result': None, 'code': DBStatusCode.RECORD_NOT_EXIST}

        async with self.__session.begin() as async_session:
            stmt = delete(Record).where(and_(
                Record.member_id == member_id,
                Record.boss_id == boss_id,
                Record.damage == damage
            ))
            await async_session.execute(stmt)

        #   Nothing is returned for removing
        return {'result': None, 'code': DBStatusCode.DELETE_SUCCESS}

    #   Search revue records from the RevueRecord identified by member_id/alias
    @debugger
    async def search_by_member(self, member_identifier: str, time_range: tuple[int, int]):
        async with self.__session.begin() as async_session:
            stmt = select(Member).options(
                selectinload(Member.records),
                with_loader_criteria(Record, and_(
                    Record.date_time >= time_range[0], Record.date_time <= time_range[1]
                ))
            ).filter(or_(
                Member.member_id == member_identifier, Member.alias == member_identifier
            ))

            query = await async_session.stream(stmt)
            member = await query.scalars().first()

        if member:
            result = []
            for record in member.records:
                result.append(self._formatter(record))

            return {'result': result, 'code': DBStatusCode.SEARCH_SUCCESS}
        else:
            return {'result': [], 'code': DBStatusCode.SEARCH_FAIL}

    #   Search revue records from the RevueRecord identified by boss_id/alias
    @debugger
    async def search_by_boss(self, boss_identifier: str, time_range: tuple[int, int]):
        try:
            boss_id = int(boss_identifier)
            boss_alias = ''
        except ValueError:
            boss_id = -1
            boss_alias = boss_identifier

        async with self.__session.begin() as async_session:
            stmt = select(Boss).options(
                selectinload(Boss.records),
                with_loader_criteria(Record, and_(
                    Record.date_time >= time_range[0], Record.date_time <= time_range[1]
                ))
            ).filter(or_(
                Boss.boss_id == boss_id, Boss.alias == boss_alias
            ))

            query = await async_session.stream(stmt)
            boss = await query.scalars().first()

        if boss:
            result = []
            for record in boss.records:
                result.append(self._formatter(record))

            return {'result': result, 'code': DBStatusCode.SEARCH_SUCCESS}
        else:
            return {'result': [], 'code': DBStatusCode.SEARCH_FAIL}

    #   Helper method for retrieving member_id
    async def _member_id_locator(self, member_identifier: str) -> str:
        async with self.__session.begin() as async_session:
            query = await async_session.stream(
                select(Member).filter(or_(Member.member_id == member_identifier, Member.alias == member_identifier))
            )
            record = await query.scalar()
        if record is None:
            return ''
        else:
            return record.member_id

    #   Helper method for retrieving boss_id
    async def _boss_id_locator(self, boss_identifier: str) -> int:
        try:
            boss_id = int(boss_identifier)
            stmt = select(Boss).filter(Boss.boss_id == boss_id)
        except ValueError:
            stmt = select(Boss).filter(Boss.alias == boss_identifier)

        async with self.__session.begin() as async_session:
            query = await async_session.stream(stmt)
            record = await query.scalar()

        if record is None:
            return -1
        else:
            return record.boss_id

    #   Helper formatter method
    @staticmethod
    def _formatter(record: Record) -> dict:
        return {
            'member_id': record.member_id,
            'boss_id': record.boss_id,
            'damage': record.damage,
            'sequence': record.sequence,
            'turn': record.turn,
            'team': record.team,
            'time': record.date_time
        }
