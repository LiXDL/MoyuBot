from pathlib import Path
import time
import datetime

import nonebot
import nonebot.typing as typing
import nonebot.permission as permission
import nonebot.adapters.cqhttp as cqhttp
import nonebot.adapters.cqhttp.permission as cpermission

from nonebot.plugin import on_command

from .config import Config
from .constants import InteractionMessage, DBStatusCode
from . import RecordDB

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

record_database = RecordDB.RecordDB(
    Path().cwd()
    .joinpath(plugin_config.company_storage)
    .joinpath(plugin_config.company_record)
    .joinpath('CompanyRevue.db')
)

helper = on_command(
    cmd='helper_record',
    aliases={'记录管理'},
    priority=10
)

add_record = on_command(
    cmd='add_record',
    aliases={'添加记录', 'ar'},
    priority=1
)

remove_record = on_command(
    cmd='remove_record',
    aliases={'删除记录', 'rr'},
    permission=permission.SUPERUSER | cpermission.GROUP_OWNER | cpermission.GROUP_ADMIN,
    priority=2
)

search_record = on_command(
    cmd='search_record',
    aliases={'搜索记录'},
    priority=10
)

search_record_by_member = on_command(
    cmd=('search_record', 'member'),
    aliases={('搜索记录', '成员'), ('sr', 'm')},
    priority=3
)

search_record_by_boss = on_command(
    cmd=('search_record', 'boss'),
    aliases={('搜索记录', 'boss'), ('sr', 'b')},
    priority=3
)


@helper.handle()
async def helper_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    await helper.finish(InteractionMessage.RECORD_MANAGER_HELP_MESSAGE)


#   Arguments should include at least boss_id: int, team: int, sequence: int, damage: int;
#   the optional arguments should be
#       turn: by default in config.default_revue_turn
#       time: by default the execution time in unix timestamp
#       member_id: by default read from sender's user_id
@add_record.handle()
async def add_record_first_receive(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    arg_list = list(map(str.strip, raw_args.split(plugin_config.separator)))

    if len(arg_list) < 4 or len(arg_list) > 7:
        #   Not enough arguments have been provided
        await add_record.finish(InteractionMessage.INVALID_ARG_NUMBER)
    elif len(arg_list) > 4:
        #   turn, time, member_id might be provided
        for arg in arg_list[4:]:
            arg_check = _single_checker(arg)
            state[arg_check[0]] = arg_check[1]

    state['base_info'] = arg_list[0:4]
    state['turn'] = state.get(
        'turn',
        plugin_config.default_revue_turn
    )
    state['time'] = state.get(
        'time',
        int(time.time())
    )
    state['member_id'] = state.get(
        'member_id',
        event.user_id
    )


@add_record.handle()
async def add_record_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    revue_info = {
        'member_id': state['member_id'],
        'boss_id': state['base_info'][0],
        'team': state['base_info'][1],
        'sequence': state['base_info'][2],
        'turn': state['turn'],
        'damage': state['base_info'][3],
        'time': state['time']
    }

    add_result = await record_database.add(revue_info)
    if add_result['status'] == DBStatusCode.INSERT_SUCCESS:
        await add_record.finish(InteractionMessage.RECORD_CHANGE_SUCCESS)
    else:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(add_result['error']))

        await add_record.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))


#   Arguments should and should only include member_id: str, boss_id: int, damage: int, in that order
@remove_record.handle()
async def remove_record_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    arg_list = list(map(str.strip, raw_args.split(plugin_config.separator)))

    if len(arg_list) != 3:
        #   Not enough arguments have been provided
        await add_record.finish(InteractionMessage.INVALID_ARG_NUMBER)

    remove_identifiers = {
        'member_id': arg_list[0],
        'boss_id': arg_list[1],
        'damage': arg_list[2]
    }

    remove_result = await record_database.remove(remove_identifiers)
    if remove_result['status'] == DBStatusCode.DELETE_SUCCESS:
        await remove_record.finish(InteractionMessage.RECORD_CHANGE_SUCCESS)
    else:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(remove_result['error']))

        await remove_record.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))


@search_record.handle()
async def search_record_helper(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    await search_record.finish(InteractionMessage.RECORD_SEARCH_HELP_MESSAGE)


@search_record_by_member.handle()
async def search_by_member_handler(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    arg_list = list(map(str.strip, raw_args.split(plugin_config.separator)))

    if len(arg_list) not in [1, 2]:
        #   Not enough arguments have been provided
        await search_record_by_member.finish(InteractionMessage.INVALID_ARG_NUMBER)

    time_range = ()
    now_date = datetime.date.today().strftime('%Y-%m-%d')
    if len(arg_list) == 1:
        time_range = (
            int(time.mktime(datetime.datetime.strptime(now_date, '%Y-%m-%d').timetuple())),
            int(time.mktime((datetime.datetime.strptime(now_date, '%Y-%m-%d') +
                             datetime.timedelta(hours=23, minutes=59, seconds=59)).timetuple()))
        )
    else:
        if arg_list[1] != '-all':
            try:
                time_slice = datetime.datetime.strptime(arg_list[1], '%Y-%m-%d')
                time_range = (
                    int(time.mktime(time_slice.timetuple())),
                    int(time.mktime((time_slice + datetime.timedelta(hours=23, minutes=59, seconds=59)).timetuple()))
                )
            except ValueError:
                await search_record_by_member.finish(InteractionMessage.INVALID_ARG)

    search_result = await record_database.search('member', arg_list[0], time_range)

    if search_result['status'] != DBStatusCode.SEARCH_SUCCESS:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(search_result['error'])
            )
        await search_record_by_member.finish(InteractionMessage.ERROR_MESSAGE)
    else:
        if not search_result['result']:
            #   No record found
            await search_record_by_member.finish(
                message=InteractionMessage.RECORD_FIND_FAIL.format(arg_list[0])
            )
        else:
            result_message = InteractionMessage.RECORD_FIND_SUCCESS.format('成员(' + arg_list[0] + ')')
            result_message = result_message + '\n'.join(map(_revue_record_member_formatter, search_result['result']))
            await search_record_by_member.finish(result_message)
            
            
@search_record_by_boss.handle()
async def search_by_boss_handler(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    arg_list = list(map(str.strip, raw_args.split(plugin_config.separator)))

    if len(arg_list) not in [1, 2]:
        #   Not enough arguments have been provided
        await search_record_by_boss.finish(InteractionMessage.INVALID_ARG_NUMBER)

    time_range = ()
    now_date = datetime.date.today().strftime('%Y-%m-%d')
    if len(arg_list) == 1:
        time_range = (
            int(time.mktime(datetime.datetime.strptime(now_date, '%Y-%m-%d').timetuple())),
            int(time.mktime((datetime.datetime.strptime(now_date, '%Y-%m-%d') +
                             datetime.timedelta(hours=23, minutes=59, seconds=59)).timetuple()))
        )
    else:
        if arg_list[1] != '-all':
            try:
                time_slice = datetime.datetime.strptime(arg_list[1], '%Y-%m-%d')
                time_range = (
                    time.mktime(time_slice.timetuple()),
                    time.mktime((time_slice + datetime.timedelta(hours=23, minutes=59, seconds=59)).timetuple())
                )
            except ValueError:
                await search_record_by_boss.finish(InteractionMessage.INVALID_ARG)

    search_result = await record_database.search('boss', arg_list[0], time_range)

    if search_result['status'] != DBStatusCode.SEARCH_SUCCESS:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(search_result['error'])
            )
        await search_record_by_boss.finish(InteractionMessage.ERROR_MESSAGE)
    else:
        if not search_result['result']:
            #   No record found
            await search_record_by_boss.finish(
                message=InteractionMessage.RECORD_FIND_FAIL.format(arg_list[0])
            )
        else:
            result_message = InteractionMessage.RECORD_FIND_SUCCESS.format('Boss(' + arg_list[0] + ')')
            result_message = result_message + '\n'.join(map(_revue_record_boss_formatter, search_result['result']))
            await search_record_by_boss.finish(result_message)


#   Check and return what each arg is
def _single_checker(arg: str):
    try:
        turn = int(arg)
        if turn > plugin_config.default_revue_turn:
            raise ValueError
        return 'turn', turn
    except ValueError:
        try:
            unix_time = int(time.mktime(time.strptime(arg, '%Y-%m-%d')))
            return 'time', unix_time
        except ValueError:
            return 'member_id', arg


#   Format a single revue record
def _revue_record_member_formatter(record: dict) -> str:
    result = '''
    使用队伍 {} 对Boss {} 造成 {} 点伤害
    第 {} 刀，消耗 {} 回合
    时间 {}'''.format(
        record['team'],
        record['boss_id'],
        record['damage'],
        record['sequence'],
        record['turn'],
        datetime.datetime.fromtimestamp(record['time']).strftime('%Y-%m-%d')
    )

    return result


#   Format a single revue record
def _revue_record_boss_formatter(record: dict) -> str:
    result = '''
    成员 {} 使用队伍 {} 造成 {} 点伤害
    第 {} 刀，消耗 {} 回合
    时间 {}'''.format(
        record['member_id'],
        record['team'],
        record['damage'],
        record['sequence'],
        record['turn'],
        datetime.datetime.fromtimestamp(record['time']).strftime('%Y-%m-%d')
    )

    return result
