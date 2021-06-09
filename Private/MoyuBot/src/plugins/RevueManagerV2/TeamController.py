from sqlalchemy import delete, update, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, selectinload

from sqlalchemy.engine import Engine
from sqlalchemy import event

from .model import Member, Team
from .constants import DBStatusCode
from .debugger import debugger


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


#   Use singleton to force single connection
class TeamController(object):
    __instance = None

    def __new__(cls, db_path: str):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__engine = create_async_engine('sqlite+aiosqlite:///' + db_path)
            cls.__session = sessionmaker(cls.__engine, expire_on_commit=False, class_=AsyncSession)
        return cls.__instance

    def __int__(self, db_path: str):
        pass

    @classmethod
    def change_database(cls, db_path: str):
        cls.__engine = create_async_engine('sqlite+aiosqlite:///' + str(db_path))
        cls.__session = sessionmaker(cls.__engine, expire_on_commit=False, class_=AsyncSession)

    #   Add a new team record to the TeamRecord
    #   The key-value pair in dict must match the parameter of Record
    #   i.e. member_id, team_id, team_list, us_list
    @debugger
    async def add(self, info: dict):
        existence = await self._search_single(info['member_id'], info['team_id'])
        if not existence:
            return {'result': None, 'code': DBStatusCode.RECORD_ALREADY_EXIST}

        async with self.__session.begin() as async_session:
            async_session.add(Team(**info))

        #   Nothing is returned for adding
        return {'result': None, 'code': DBStatusCode.INSERT_SUCCESS}

    #   Delete a team record from the RevueRecord
    #   Deletion is performed based on member_id/alias and team_id
    @debugger
    async def delete(self, member_identifier: str, team_id: int):
        existence = await self._search_single(member_identifier, team_id)
        if not existence:
            return {'result': None, 'code': DBStatusCode.RECORD_NOT_EXIST}

        async with self.__session.begin() as async_session:
            stmt = delete(Team).where(and_(
                or_(Member.member_id == member_identifier, Member.alias == member_identifier),
                Team.team_id == team_id
            ))
            await async_session.execute(stmt)

        #   Nothing is returned for removing
        return {'result': None, 'code': DBStatusCode.DELETE_SUCCESS}

    #   Update a team record in the CompanyInfo
    #   The key-value pairs in dict must match the parameter of Team
    #   i.e. member_id, team_id, team_list, us_list
    @debugger
    async def update(self, info: dict):
        existence = await self._search_single(info['member_id'], info['team_id'])
        if not existence:
            return {'result': None, 'code': DBStatusCode.RECORD_NOT_EXIST}

        async with self.__session.begin() as async_session:
            stmt = update(Team).where(
                and_(
                    Member.member_id == info['member_id'],
                    Team.team_id == info['team_id']
                )
            ).values(**info)
            await async_session.execute(stmt)

        return {'result': None, 'code': DBStatusCode.UPDATE_SUCCESS}

    #   Search a single team record in the CompanyInfo
    @debugger
    async def search_team(self, member_identifier: str, team_id: int):
        team = await self._search_single(member_identifier, team_id)
        if not team:
            return {'result': [], 'code': DBStatusCode.RECORD_NOT_EXIST}
        else:
            return {'result': self._formatter(team), 'code': DBStatusCode.SEARCH_SUCCESS}

    #   Search team records for a member in the CompanyInfo
    @debugger
    async def search_member(self, member_identifier: str):
        async with self.__session.begin() as async_session:
            stmt = select(Member).options(
                selectinload(Member.teams)
            ).filters(
                or_(
                    Member.member_id == member_identifier,
                    Member.alias == member_identifier
                )
            )
            query = await async_session.stream(stmt)
            member = await query.scalars().first()

        if member:
            result = []
            for team in member.records:
                result.append(self._formatter(team))

            return {'result': result, 'code': DBStatusCode.SEARCH_SUCCESS}
        else:
            return {'result': [], 'code': DBStatusCode.SEARCH_FAIL}

    #   Helper method for searching team record
    async def _search_single(self, member_identifier: str, team_id: int) -> Team:
        async with self.__session.begin() as async_session:
            query = await async_session.stream(
                select(Team).filter(
                    and_(
                        or_(Member.member_id == member_identifier, Member.alias == member_identifier),
                        Team.team_id == team_id
                    )
                ).order_by(Team.record_id.asc())
            )
            result = await query.scalars().first()
        return result

    @staticmethod
    def _formatter(team: Team) -> dict:
        return {
            'member_id': team.member_id,
            'team_id': team.team_id,
            'team_list': team.team_list,
            'us_list': team.us_list
        }
