import aiosqlite
from pathlib import Path
from .model import DBStatusCode


class BossDB:

    #   database must exist and be a .db file
    def __init__(self, database: Path):
        self._database = database

    #   Add record to BossInfo
    #   :param: must include {id: int, alias: str, health: int}
    async def add(self, info: dict):
        record = (
            int(info['id']),
            str(info['alias']).encode('utf8'),
            int(info['health'])
        )
        insert_phrase = '''
        INSERT INTO BossInfo VALUES(?, ?, ?);
        '''

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

    #   Delete record from BossInfo
    #   :param: must only be id
    async def remove(self, boss_id: int):
        remove_phrase = '''
        DELETE FROM BossInfo
        WHERE id = ?;
        '''

        async with aiosqlite.connect(self._database) as conn:
            try:
                await conn.execute(remove_phrase, (boss_id, ))
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

    #   Update record in CompanyInfo
    #   :param: must include {id: int, alias: str, health: int}
    async def update(self, info):
        record = (
            str(info['alias']).encode('utf8'),
            int(info['health']),
            int(info['id'])
        )
        update_phrase = '''
        UPDATE BossInfo
        SET alias = ?, health = ?
        WHERE id = ?;
        '''

        async with aiosqlite.connect(self._database) as conn:
            try:
                await conn.execute(update_phrase, record)
                await conn.commit()
                return {
                    'status': DBStatusCode.UPDATE_SUCCESS,
                    'error': None
                }
            except aiosqlite.Error as sqlerror:
                return {
                    'status': DBStatusCode.UPDATE_FAIL,
                    'error': sqlerror
                }
            except Exception as e:
                return {
                    'status': DBStatusCode.UNKNOWN_ERROR,
                    'error': e
                }

    #   Search record in BossInfo
    #   :param: identifier: str, represents either id or alias
    #   empty input will be considered as no match
    async def search(self, identifier: str):
        if identifier is None or identifier == '':
            return {
                'status': DBStatusCode.SEARCH_SUCCESS,
                'error': None,
                'result': {}
            }

        #   Check identifier is id or alias
        try:
            search_phrase = '''
            SELECT * FROM BossInfo
            WHERE id = ?;
            '''
            search_param = int(identifier)
        except ValueError:
            search_phrase = '''
            SELECT * FROM BossInfo
            WHERE alias = ?;
            '''
            search_param = str(identifier).encode('utf8')

        async with aiosqlite.connect(self._database) as conn:
            try:
                async with conn.execute(search_phrase, (search_param, )) as cursor:
                    record = await cursor.fetchone()
                    if record:
                        result = {
                            'id': int(record[0]),
                            'alias': bytes(record[1]).decode('utf8'),
                            'health': int(record[2])
                        }
                        return {
                            'status': DBStatusCode.SEARCH_SUCCESS,
                            'error': None,
                            'result': result
                        }
                    else:
                        return {
                            'status': DBStatusCode.SEARCH_SUCCESS,
                            'error': None,
                            'result': {}
                        }
            except aiosqlite.Error as sqlerror:
                return {
                    'status': DBStatusCode.SEARCH_FAIL,
                    'error': sqlerror,
                    'result': {}
                }
            except Exception as e:
                return {
                    'status': DBStatusCode.UNKNOWN_ERROR,
                    'error': e,
                    'result': {}
                }

    #   List all records in CompanyInfo
    async def display(self):
        search_phrase = '''
        SELECT * FROM BossInfo
        ORDER BY id;
        '''
        result = []

        async with aiosqlite.connect(self._database) as conn:
            try:
                async with conn.execute(search_phrase) as cursor:
                    records = await cursor.fetchall()
                    for record in records:
                        result.append({
                            'id': int(record[0]),
                            'alias': bytes(record[1]).decode('utf8'),
                            'health': int(record[2])
                        })
                return {
                    'status': DBStatusCode.SEARCH_SUCCESS,
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
