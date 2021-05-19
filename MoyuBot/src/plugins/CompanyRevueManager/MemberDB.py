import aiosqlite
from pathlib import Path
from .model import DBStatusCode


class MemberDB:

    #   database must exist and be a .db file
    def __init__(self, database: Path):
        self._database = database

    #   Add record to CompanyInfo
    #   :param: must include {id: str, alias: str, account: str, password: str}
    async def add(self, info: dict):
        record = (
            str(info['id']),
            str(info['alias']).encode('utf8'),
            str(info['account']),
            str(info['password'])
        )
        insert_phrase = '''
        INSERT INTO CompanyInfo VALUES(?, ?, ?, ?);
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

    #   Delete record from CompanyInfo
    #   :param: must only be id
    async def remove(self, member_id: str):
        remove_phrase = '''
        DELETE FROM CompanyInfo 
        WHERE id = ?;
        '''

        async with aiosqlite.connect(self._database) as conn:
            try:
                await conn.execute(remove_phrase, (member_id, ))
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
    #   :param: must include {id: str, alias: str, account: str, password: str}
    async def update(self, info):
        record = (
            str(info['alias']).encode('utf8'),
            str(info['account']),
            str(info['password']),
            str(info['id'])
        )
        update_phrase = '''
        UPDATE CompanyInfo
        SET alias = ?, account = ?, password = ? 
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

    #   Search record in CompanyInfo
    #   :param: identifier: str, represents either id or alias
    #   empty input will be considered as no match
    async def search(self, identifier: str):
        if identifier is None or identifier == '':
            return {
                'status': DBStatusCode.SEARCH_SUCCESS,
                'error': None,
                'result': {}
            }

        search_phrase = '''
        SELECT * FROM CompanyInfo
        WHERE id = ?
        OR alias = ?; 
        '''
        search_param = (identifier, identifier.encode('utf8'))

        async with aiosqlite.connect(self._database) as conn:
            try:
                async with conn.execute(search_phrase, search_param) as cursor:
                    record = await cursor.fetchone()
                    if record:
                        result = {
                            'id': str(record[0]),
                            'alias': bytes(record[1]).decode('utf8'),
                            'account': str(record[2]),
                            'password': str(record[3])
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
        SELECT * FROM CompanyInfo
        ORDER BY id;
        '''
        result = []

        async with aiosqlite.connect(self._database) as conn:
            try:
                async with conn.execute(search_phrase) as cursor:
                    records = await cursor.fetchall()
                    for record in records:
                        result.append({
                            'id': str(record[0]),
                            'alias': bytes(record[1]).decode('utf8'),
                            'account': str(record[2]),
                            'password': str(record[3])
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
