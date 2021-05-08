import aiosqlite
from pathlib import Path
from MoyuBot.src.plugins.CompanyRevueManager.model import DBStatusCode


class MemberDB:

    #   database must exist and be a .db file
    def __init__(self, database: Path):
        self._database = database

    #   Add record to CompanyInfo
    #   :param: must include {id: str, alias: str, account: str, password: str}
    async def add(self, **kwargs):

        record = (
            str(kwargs['id']),
            str(kwargs['alias']).encode('utf8'),
            str(kwargs['account']),
            str(kwargs['password'])
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
                await conn.close()
                return {
                    'status': DBStatusCode.INSERT_FAIL,
                    'error': sqlerror
                }
            except Exception as e:
                await conn.close()
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
                await conn.close()
                return {
                    'status': DBStatusCode.DELETE_FAIL,
                    'error': sqlerror
                }
            except Exception as e:
                await conn.close()
                return {
                    'status': DBStatusCode.UNKNOWN_ERROR,
                    'error': e
                }

    #   Update record in CompanyInfo
    #   :param: must include {id: str, alias: str, account: str, password: str}
    async def update(self, **kwargs):

        record = (
            str(kwargs['alias']).encode('utf8'),
            str(kwargs['account']),
            str(kwargs['password']),
            str(kwargs['id'])
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
                await conn.close()
                return {
                    'status': DBStatusCode.UPDATE_FAIL,
                    'error': sqlerror
                }
            except Exception as e:
                await conn.close()
                return {
                    'status': DBStatusCode.UNKNOWN_ERROR,
                    'error': e
                }

    #   Search record in CompanyInfo
    #   :param: member_id: str, alias: str, member_id is first used if available
    #   empty input will be considered as unavailable
    #   member_id and alias should not be empty simultaneously
    async def search(self, member_id: str, alias: str):
        if member_id != '':
            #   Use member_id to search
            search_phrase = '''
            SELECT * FROM CompanyInfo
            WHERE id = ?;
            '''
            search_param = (member_id, )
        else:
            #   Use alias to search
            search_phrase = '''
            SELECT * FROM CompanyInfo
            WHERE alias = ?;
            '''
            search_param = (alias.encode('utf8'), )

        async with aiosqlite.connect(self._database) as conn:
            try:
                async with conn.execute(search_phrase, search_param) as cursor:
                    record = cursor.fetchone()
                    if record:
                        result = {
                            'id': str(record['id']),
                            'alias': bytes(record['alias']).decode('utf8'),
                            'account': str(record['account']),
                            'password': str(record['password'])
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
                await conn.close()
                return {
                    'status': DBStatusCode.SEARCH_FAIL,
                    'error': sqlerror,
                    'result': {}
                }
            except Exception as e:
                await conn.close()
                return {
                    'status': DBStatusCode.UNKNOWN_ERROR,
                    'error': e,
                    'result': {}
                }

    #   List all records in CompanyInfo
    async def display(self):
        search_phrase = '''
        SELECT * FROM CompanyInfo;
        '''
        result = []

        async with aiosqlite.connect(self._database) as conn:
            try:
                async with conn.execute(search_phrase) as cursor:
                    async for record in cursor:
                        result.append({
                            'id': str(record['id']),
                            'alias': bytes(record['alias']).decode('utf8'),
                            'account': str(record['account']),
                            'password': str(record['password'])
                        })
            except aiosqlite.Error as sqlerror:
                await conn.close()
                return {
                    'status': DBStatusCode.SEARCH_FAIL,
                    'error': sqlerror,
                    'result': []
                }
            except Exception as e:
                await conn.close()
                return {
                    'status': DBStatusCode.UNKNOWN_ERROR,
                    'error': e,
                    'result': []
                }
