import asyncio
import json
import time

import aiofiles
import aiohttp
import aiosqlite

from pathlib import Path
from MoyuBot.src.plugins.GameResourceManager.model import DBSCode


#   Requests from url
async def request(url):
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
#   :param record: list of inserted values, assumed to be following the insertion order with length 17
async def write_card_info(database: Path, record: list):
    async with aiosqlite.connect(database) as aio_conn:
        try:
            await aio_conn.execute('''
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
            '''.format(', '.join(['?'] * 17)), record)

            await aio_conn.commit()

            return {'status': DBSCode.SUCCESS, 'error_message': None}
        except aiosqlite.Error as e:
            pass
            return {'status': DBSCode.INSERTION_ERROR, 'error_message': e}


#   Write to Card Skill directory
#   Generate two corresponding JSON files
#   Use pathlib.Path to access certain path.
async def write_card_skill(active_path: Path, active_skill, passive_path: Path, passive_skill, card_id: str):
    active_file = active_path.joinpath(card_id + '.json')
    passive_file = passive_path.joinpath(card_id + '.json')

    async with aiofiles.open(active_file, 'w') as f:
        await f.write(json.dumps(active_skill))

    async with aiofiles.open(passive_file, 'w') as f:
        await f.write(json.dumps(passive_skill))

    return {'Status': DBSCode.SUCCESS}


#   Separate and format original JSON file for storing
def split(dress: dict):
    result_sqlite = []

    card_id = int(dress['basicInfo']['cardID'])
    result_sqlite.append(card_id)

    name = str(dress['basicInfo']['name']['ja']).encode('utf8')
    result_sqlite.append(name)

    release = int(dress['basicInfo']['released']['ja'])
    result_sqlite.append(release)

    char_id = int(dress['basicInfo']['character'])
    result_sqlite.append(char_id)

    school_id = int(char_id / 100)
    result_sqlite.append(school_id)

    rarity = int(dress['basicInfo']['rarity'])
    result_sqlite.append(rarity)

    class_ = int(dress['base']['attribute'])
    result_sqlite.append(class_)

    attack_type = int(dress['base']['attackType'])
    result_sqlite.append(attack_type)

    role = str(dress['base']['roleIndex']['role']).encode('utf8')
    result_sqlite.append(role)

    position = int(dress['base']['roleIndex']['index'])
    result_sqlite.append(position)

    total = int(dress['stat']['total'])
    result_sqlite.append(total)

    speed = int(dress['stat']['agi'])
    result_sqlite.append(speed)

    attack = int(dress['stat']['atk'])
    result_sqlite.append(attack)

    health = int(dress['stat']['hp'])
    result_sqlite.append(health)

    magic_def = int(dress['stat']['mdef'])
    result_sqlite.append(magic_def)

    physical_def = int(dress['stat']['pdef'])
    result_sqlite.append(physical_def)

    crit_chance = int(dress['other']['dex'])
    result_sqlite.append(crit_chance)

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


async def grab_one_card(card_id: str):
    url = 'https://karth.top/api/dress/{}.json'.format(card_id)
    data_path = Path().cwd().parent.parent.parent.joinpath('Data').joinpath('Card')

    card_info = await request(url)
    print('Fetching card {}'.format(card_id))

    result = card_info['result']
    if result:
        print('Found info for card {}'.format(card_id))
        split_result = split(result)

        card_stat_result = await write_card_info(data_path.joinpath('Card.db'), split_result['stats'])
        card_skill_result = await write_card_skill(
            data_path.joinpath('Skill').joinpath('Active'),
            split_result['active'],
            data_path.joinpath('Skill').joinpath('Passive'),
            split_result['passive'],
            card_id
        )
    else:
        print('No info for card {}'.format(card_id))

    return None


def single_test():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(grab_one_card('4020011'))


def multi_test(max_card_num=30):
    start = time.time()

    dress_list = []
    for school in [1, 2, 3, 4, 5]:
        for character in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            for i in range(1, max_card_num + 1):
                dress_list.append(str(int(school*1e6 + character*1e4 + i)))

    loop = asyncio.get_event_loop()
    tasks = []
    for dress in dress_list:
        task = loop.create_task(grab_one_card(dress))
        tasks.append(task)

    loop.run_until_complete(asyncio.gather(*tasks))

    end = time.time()
    print('Time spend: {}'.format(end - start))


if __name__ == '__main__':
    multi_test()
