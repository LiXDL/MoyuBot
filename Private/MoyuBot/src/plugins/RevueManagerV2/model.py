#   ORM database model and initialization

from pathlib import Path
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import relationship



Base = declarative_base()
DB_FILE = Path.cwd().parent.parent.parent.joinpath('Data/Company').joinpath('ORMTest').joinpath('Revue.db')


class Member(Base):
    __tablename__ = "CompanyInfo"

    member_id = Column(String, primary_key=True)
    alias = Column(String)
    account = Column(String)
    password = Column(String)

    def __init__(self, member_id: str, alias: str, account: str, password: str):
        self.member_id = member_id
        self.alias = alias
        self.account = account
        self.password = password

    def __repr__(self):
        return '<Member (id:{}, alias:{}, account:{}, password: {})>'.format(
            self.member_id, self.alias, self.account, self.password
        )


class Boss(Base):
    __tablename__ = "BossInfo"

    boss_id = Column(Integer, primary_key=True)
    alias = Column(String)
    health = Column(Integer)

    def __init__(self, boss_id, alias, health):
        self.boss_id = boss_id
        self.alias = alias
        self.health = health

    def __repr__(self):
        return '<Boss (id:{}, alias:{}, health:{})>'.format(
            self.boss_id, self.alias, self.health
        )


class Record(Base):
    __tablename__ = "RevueRecord"

    record_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String, ForeignKey("CompanyInfo.member_id", onupdate='CASCADE', ondelete='NO ACTION'))
    boss_id = Column(Integer, ForeignKey("BossInfo.boss_id", onupdate='CASCADE', ondelete='NO ACTION'))
    damage = Column(Integer)
    sequence = Column(Integer)
    turn = Column(Integer)
    team = Column(Integer)
    date_time = Column(Integer)

    member = relationship("MemberInfo", backref="member_revue_record",)
    boss = relationship("BossInfo", backref="boss_revue_record")

    def __init__(self, member_id: str, boss_id: int, damage: int, sequence: int, turn: int, team: int, date_time: int):
        self.member_id = member_id
        self.boss_id = boss_id
        self.damage = damage
        self.sequence = sequence
        self.turn = turn
        self.team = team
        self.date_time = date_time

    def __repr__(self):
        return '<RevueRecord (id: {}, member_id: {}, boss_id: {}, damage: {}, sequence: {}, ' \
               'turn: {}, team: {}, date_time: {})>'.format(
                self.record_id, self.member_id, self.boss_id, self.damage, self.sequence,
                self.turn, self.team, self.date_time)


class Team(Base):
    __tablename__ = "TeamRecord"

    record_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String, ForeignKey("CompanyInfo.member_id", onupdate='CASCADE', ondelete='NO ACTION'))
    team_id = Column(Integer)
    team_list = Column(String)
    us_list = Column(String)

    member = relationship("MemberInfo", backref='member_team')

    def __init__(self, member_id: str, team_id: int, team_list: str, us_list: str):
        self.member_id = member_id
        self.team_id = team_id
        self.team_list = team_list
        self.us_list = us_list

    def __repr__(self):
        return '<TeamRecord (id: {}, member_id: {}, team_id: {}, team_list: [{}], us_list: [{}])>'.format(
            self.record_id, self.member_id, self.team_id, self.team_list, self.us_list
        )


async def _reset_database():
    aioengine = create_async_engine('sqlite+aiosqlite:///' + str(DB_FILE), echo=True)

    async with aioengine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)



