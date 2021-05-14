import aiosqlite
from pathlib import Path
from .model import DBStatusCode


class RecordDB:

    #   database must exist and be a .db file
    def __init__(self, database: Path):
        self._database = database

    #   Add record to RevueRecord
    #   :param: {
    #       member_id: str, boss_id: int, team: int, (member, boss related)
    #       sequence: int, turn: int, remain_turn: int, (record related)
    #       damage：int,
    #       time: int (datetime unix timestamp)
    #   }
    async def add(self, info: dict):
        record = (
            None,   # Placeholder for autoincrement ID
            str(info['member_id']),
            int(info['boss_id']),
            int(info['team']),
            int(info['sequence']),
            int(info['turn']),
            int(info['remain_turn']),
            int(info['damage']),
            int(info['time'])
        )
        insert_phrase = '''
        INSERT INTO RevueRecord VALUES ({});
        '''.format(', '.join(['?'] * len(record)))

        async with aiosqlite.connect(self._database) as conn:
            try:
                await conn.execute(insert_phrase, record)
                await conn.commit()
                return {
                    'status': DBStatusCode.INSERT_SUCCESS,
                    'error': None
                }
            except aiosqlite.Error as sqlerror:
                return {
                    'status': DBStatusCode.INSERT_FAIL,
                    'error': sqlerror
                }
            except Exception as e:
                return {
                    'status': DBStatusCode.UNKNOWN_ERROR,
                    'error': e
                }

    #   Delete record from RevueRecord
    #   :param: must include {member_id: text, boss_id: int, damage: int}
    async def remove(self, damage_record: dict):
        record = [
            str(damage_record['member_id']),
            int(damage_record['boss_id']),
            int(damage_record['damage'])
        ]
        remove_phrase = '''
        DELETE FROM BossInfo
        WHERE member_id = ?
        AND boss_id = ?
        AND damage = ?;
        '''

        async with aiosqlite.connect(self._database) as conn:
            try:
                await conn.execute(remove_phrase, record)
                await conn.commit()
                return {
                    'status': DBStatusCode.DELETE_SUCCESS,
                    'error': None
                }
            except aiosqlite.Error as sqlerror:
                return {
                    'status': DBStatusCode.DELETE_FAIL,
                    'error': sqlerror
                }
            except Exception as e:
                return {
                    'status': DBStatusCode.UNKNOWN_ERROR,
                    'error': e
                }

    #   Search record(s) from RevueRecord
    #   :param: keyword: 'member' | 'boss'
    #   :param: identifier: int
    #           member_id/member_alias corresponds to keywords = member
    #           boss_id/boss_alias corresponds to keyword = boss
    #   :param: time_range (start_time, end_time) inclusive
    async def search(self, keyword: str, identifier: str, time_range: tuple = ()):
        if keyword == 'member':
            search_phrase = '''
            SELECT r.*
            FROM CompanyInfo as c, RevueRecord as r
            WHERE c.id = r.member_id
            AND (c.id = ? OR c.alias = ?)
            '''
            search_param = (str(identifier), str(identifier).encode('utf8'))
        else:   # keyword == 'boss'
            search_phrase = '''
            SELECT r.*
            FROM BossInfo as b, RevueRecord as r
            WHERE b.id = r.boss_id
            AND (b.id = ? OR b.alias = ?)
            '''
            search_param = (str(identifier), str(identifier).encode('utf8'))

        if not time_range:
            search_phrase = search_phrase + '\n AND (r.time BETWEEN ? AND ?)'
            search_param = search_param + time_range

        result = []

        async with aiosqlite.connect(self._database) as conn:
            try:
                async with conn.execute(search_phrase, search_param) as cursor:
                    records = await cursor.fetchall()
                    for record in records:
                        result.append(
                            dict(zip(record.keys(), tuple(record)))
                        )

                    return {
                        'status': DBStatusCode.SEARCH_FAIL,
                        'error': None,
                        'result': result
                    }
            except aiosqlite.Error as sqlerror:
                return {
                    'status': DBStatusCode.SEARCH_FAIL,
                    'error': sqlerror,
                    'result': []
                }
            except Exception as e:
                return {
                    'status': DBStatusCode.UNKNOWN_ERROR,
                    'error': e,
                    'result': []
                }
