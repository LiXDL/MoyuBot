import asyncio
import json
import aiofiles
import aiohttp
import aiosqlite
import traceback

from .constants import DBSCode


class Scraper(object):
    __instance = None

    def __new__(cls, db_path: str):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__conn = aiosqlite.connect(db_path, isolation_level='IMMEDIATE')
        return cls.__instance

    def __init__(self, db_path: str):
        pass

    #   :param: urls:
    #       should include data_url corresponding to json format data
    #       and image_url corresponding to image data
    #   :param: paths:
    #       should include active, passive, and image storing file names in str
    async def grab_card_info(self, card_id: int, urls: dict, files: dict):
        result = {'card': None, 'error': None}

        try:
            raw_data = await self._fetch_card_info(urls['data_url'])
            if raw_data['result']:
                #   There is something grabbed from the url,
                #   i.e., there is a card corresponds to the given card_id

                #   Separate card data
                temp = self._split(raw_data['result'])
                stats = temp['stats']
                active = temp['active']
                passive = temp['passive']

                await self._write_card_info(stats)
                await self._write_card_skill(files['active'], active, files['passive'], passive)

                image_content = await self._fetch_card_art(urls['image_url'])
                await self._write_card_art(files['image'], image_content)

                result['card'] = (card_id, stats[1])
        except Exception as e:
            result['error'] = traceback.format_exc()
        finally:
            return result

    #   Requests from url
    @staticmethod
    async def _fetch_card_info(url):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            status = response.status
            await asyncio.sleep(0.1)

            if status != 200:
                return {'result': {}}
            else:
                result = await response.json()
                return {'result': result}

    #   Write to Card sqlite
    #   :param database: the database file to be connected
    #   :param record: list of inserted values, assumed to be following the insertion order
    async def _write_card_info(self, record: list):
        try:
            await self.__conn.execute('''
            INSERT INTO CardInfo (
            id, 
            name, 
            release, 
            char_id, 
            school_id, 
            rarity, 
            class, 
            attack_type, 
            role, 
            position, 
            total, 
            speed, 
            attack, 
            health, 
            magic_def, 
            physical_def, 
            critical_chance, 
            critical_damage) 
            VALUES ({})
            '''.format(', '.join(['?'] * len(record))), record)

            await self.__conn.commit()

            return {'status': DBSCode.SUCCESS, 'error_message': None}
        except aiosqlite.Error as e:
            pass
            return {'status': DBSCode.INSERTION_ERROR, 'error_message': e}

    #   Write to Card Skill directory
    #   Generate two corresponding JSON files
    #   Use pathlib.Path to access certain path.
    #   :param active_file_name: file for storing active skills
    #   :param active_skill: dict storing active skills
    #   :param passive_file_name: file for storing passive skills
    #   :param passive_skill: dict storing passive skills
    @staticmethod
    async def _write_card_skill(
            active_file_name: str, active_skill: dict,
            passive_file_name: str, passive_skill: dict
    ):
        async with aiofiles.open(active_file_name, 'w') as f:
            await f.write(json.dumps(active_skill))

        async with aiofiles.open(passive_file_name, 'w') as f:
            await f.write(json.dumps(passive_skill))

        return {'Status': DBSCode.SUCCESS}

    #   Get card Art image
    @staticmethod
    async def _fetch_card_art(url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image_content = await response.read()
                    return {'image': image_content}
                else:
                    return {'image': None}

    #   Store card Art image to the given directory with id as name
    @staticmethod
    async def _write_card_art(art_file_name: str, image):
        async with aiofiles.open(art_file_name, 'wb') as f:
            await f.write(image)
            return DBSCode.SUCCESS

    #   Separate and format original JSON file for storing
    @staticmethod
    def _split(dress: dict):
        result_sqlite = []

        #   0
        card_id = int(dress['basicInfo']['cardID'])
        result_sqlite.append(card_id)

        #   1
        name = str(dress['basicInfo']['name']['ja']).encode('utf8')
        result_sqlite.append(name)

        #   2
        release = int(dress['basicInfo']['released']['ja'])
        result_sqlite.append(release)

        #   3
        char_id = int(dress['basicInfo']['character'])
        result_sqlite.append(char_id)

        #   4
        school_id = int(char_id / 100)
        result_sqlite.append(school_id)

        #   5
        rarity = int(dress['basicInfo']['rarity'])
        result_sqlite.append(rarity)

        #   6
        class_ = int(dress['base']['attribute'])
        result_sqlite.append(class_)

        #   7
        attack_type = int(dress['base']['attackType'])
        result_sqlite.append(attack_type)

        #   8
        role = str(dress['base']['roleIndex']['role']).encode('utf8')
        result_sqlite.append(role)

        #   9
        position = int(dress['base']['roleIndex']['index'])
        result_sqlite.append(position)

        #   10
        total = int(dress['stat']['total'])
        result_sqlite.append(total)

        #   11
        speed = int(dress['stat']['agi'])
        result_sqlite.append(speed)

        #   12
        attack = int(dress['stat']['atk'])
        result_sqlite.append(attack)

        #   13
        health = int(dress['stat']['hp'])
        result_sqlite.append(health)

        #   14
        magic_def = int(dress['stat']['mdef'])
        result_sqlite.append(magic_def)

        #   15
        physical_def = int(dress['stat']['pdef'])
        result_sqlite.append(physical_def)

        #   16
        crit_chance = int(dress['other']['dex'])
        result_sqlite.append(crit_chance)

        #   17
        crit_damage = int(dress['other']['cri'])
        result_sqlite.append(crit_damage)

        active_skill = {
            'act1': dress['act']['act1'],
            'act2': dress['act']['act2'],
            'act3': dress['act']['act3'],
            'climax': dress['groupSkills']['climaxACT']
        }

        passive_skill = {
            'auto_skill': dress['skills'],
            'unit_skill': dress['groupSkills']['unitSkill'],
            'finish_act': dress['groupSkills']['finishACT']
        }

        return {'stats': result_sqlite, 'active': active_skill, 'passive': passive_skill}

#   Deprecated functional tests
#
#
#
# async def grab_one_card(card_id: str):
#     url = 'https://karth.top/api/dress/{}.json'.format(card_id)
#     data_path = Path().cwd().parent.parent.parent.joinpath('Data').joinpath('Card')
#
#     card_info = await fetch_card_info(url)
#     print('Fetching card {}'.format(card_id))
#
#     result = card_info['result']
#     if result:
#         print('Found info for card {}'.format(card_id))
#         split_result = split(result)
#
#         card_stat_result = await write_card_info(data_path.joinpath('Card.db'), split_result['stats'])
#         card_skill_result = await write_card_skill(
#             data_path.joinpath('Skill').joinpath('Active'),
#             split_result['active'],
#             data_path.joinpath('Skill').joinpath('Passive'),
#             split_result['passive'],
#             card_id
#         )
#     else:
#         print('No info for card {}'.format(card_id))
#
#     return None
#
#
# def single_test():
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(grab_one_card('4020011'))
#
#
# def multi_test(max_card_num=30):
#     start = time.time()
#
#     dress_list = []
#     for school in [1, 2, 3, 4, 5]:
#         for character in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
#             for i in range(1, max_card_num + 1):
#                 dress_list.append(str(int(school*1e6 + character*1e4 + i)))
#
#     loop = asyncio.get_event_loop()
#     tasks = []
#     for dress in dress_list:
#         task = loop.create_task(grab_one_card(dress))
#         tasks.append(task)
#
#     loop.run_until_complete(asyncio.gather(*tasks))
#
#     end = time.time()
#     print('Time spend: {}'.format(end - start))
#
#
# def grab_one_image():
#     url = 'https://api.karen.makoo.eu/api/assets/dlc/res/dress/cg/{}/image.png'
#     art_path = Path().cwd().parent.parent.parent.joinpath('Data').joinpath('Card').joinpath('Art')
#
#     loop = asyncio.get_event_loop()
#     task = loop.create_task(fetch_card_art(url.format('2020020')))
#     loop.run_until_complete(task)
#     print('image: {}'.format(task.result()))
#
#
# if __name__ == '__main__':
#     grab_one_image()
