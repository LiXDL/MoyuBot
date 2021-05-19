from pathlib import Path

import nonebot
import nonebot.typing as typing
import nonebot.permission as permission
import nonebot.adapters.cqhttp as cqhttp
import nonebot.adapters.cqhttp.permission as cpermission

from nonebot.plugin import on_command

from .config import Config
from .model import InteractionMessage, DBStatusCode
from . import BossDB

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

boss_database = BossDB.BossDB(
    Path().cwd()
    .joinpath(plugin_config.company_storage)
    .joinpath(plugin_config.company_record)
    .joinpath('CompanyRevue.db')
)

helper = on_command(
    cmd='help_boss',
    aliases={'boss管理'},
    priority=10
)

add_boss = on_command(
    cmd='add_boss',
    aliases={'添加boss', 'ab'},
    permission=permission.SUPERUSER | cpermission.GROUP_OWNER | cpermission.GROUP_ADMIN,
    priority=1
)

add_boss_range = on_command(
    cmd='add_boss_range',
    aliases={'添加boss组', 'abr'},
    permission=permission.SUPERUSER | cpermission.GROUP_OWNER | cpermission.GROUP_ADMIN,
    priority=1
)

remove_boss = on_command(
    cmd='remove_boss',
    aliases={'移除boss', 'rb'},
    permission=permission.SUPERUSER | cpermission.GROUP_OWNER | cpermission.GROUP_ADMIN,
    priority=2
)

update_boss = on_command(
    cmd='update_boss',
    aliases={'更新boss', 'ub'},
    permission=permission.SUPERUSER | cpermission.GROUP_OWNER | cpermission.GROUP_ADMIN,
    priority=3
)

search_boss = on_command(
    cmd='search_boss',
    aliases={'搜索boss', 'sb'},
    priority=4
)

list_boss = on_command(
    cmd='list_boss',
    aliases={'boss列表', 'lb'},
    priority=4
)


@helper.handle()
async def helper_handler(bot: cqhttp.Bot, event: cqhttp.Event):
    await helper.finish(InteractionMessage.BOSS_MANAGER_HELP_MESSAGE)


@add_boss.args_parser
async def add_boss_parser(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    state[state['_current_key']] = str(event.get_message()).strip().split(plugin_config.separator)


@add_boss.handle()
async def add_boss_first_receive(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    if raw_args:
        arg_list = raw_args.split(plugin_config.separator)
        state['info'] = arg_list


@add_boss.got('info', prompt=InteractionMessage.REQUEST_ARG)
async def add_boss_handler(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    #   Check if all 3 info are provided
    if len(state['info']) != 3:
        await add_boss.finish(
            message=InteractionMessage.INVALID_ARG_NUMBER
        )

    info = {
        'id': int(str(state['info'][0]).strip()),
        'alias': str(state['info'][1]).strip(),
        'health': int(str(state['info'][2]).strip())
    }

    add_result = await boss_database.add(info)
    if add_result['status'] == DBStatusCode.INSERT_SUCCESS:
        await add_boss.finish(InteractionMessage.RECORD_CHANGE_SUCCESS)
    else:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(add_result['error']))

        await add_boss.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))


#   Should contain boss names, boss healths, start_level(inclusive), end_level(exclusive)
#   which are total 10 arguments
@add_boss_range.handle()
async def add_boss_range_handler(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    arg_list = list(map(str.strip, raw_args.split(plugin_config.separator)))

    boss_names = arg_list[0:4]
    boss_healths = list(map(int, arg_list[4:8]))
    start_level = int(arg_list[8])
    end_level = int(arg_list[9])

    for level in range(start_level, end_level):
        for i in range(len(boss_names)):
            info = {
                'id': level * 100 + i + 1,
                'alias': 'R' + str(level) + boss_names[i],
                'health': boss_healths[i]
            }
            await boss_database.add(info)

    await add_boss_range.finish(
        message='Added Boss in level range {} and {}'.format(start_level, end_level)
    )


@remove_boss.args_parser
async def remove_boss_parser(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    state[state['_current_key']] = int(str(event.get_message()).strip())


@remove_boss.handle()
async def remove_boss_first_receive(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    if raw_args:
        state['boss_id'] = int(raw_args)


@remove_boss.got('boss_id', prompt=InteractionMessage.REQUEST_ARG)
async def remove_boss_requester(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    #   Check if the provided boss_id is in the records
    search_result = await boss_database.search(state['boss_id'])

    if search_result['status'] != DBStatusCode.SEARCH_SUCCESS:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(search_result['error'])
            )
        await remove_boss.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))
    else:
        if search_result['result']:
            #   Record found, ask for confirmation
            await remove_boss.pause(
                prompt='\n'.join([
                    InteractionMessage.RECORD_FIND_SUCCESS.format(state['boss_id']),
                    InteractionMessage.REQUEST_CONFIRM
                ])
            )
        else:
            #   Record not found
            await remove_boss.finish(
                message='\n'.join([
                    InteractionMessage.RECORD_FIND_FAIL.format(state['boss_id']),
                    InteractionMessage.RECORD_CHANGE_FAIL
                ])
            )


@remove_boss.handle()
async def remove_boss_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    #   Request valid confirmation for deletion
    while True:
        if str(event.get_message()).strip() not in InteractionMessage.CONFIRMATION_MESSAGE:
            await remove_boss.reject(InteractionMessage.INVALID_ARG)
        else:
            break

    user_confirm = str(event.get_message()).strip()
    if user_confirm.startswith(InteractionMessage.CONFIRMATION_MESSAGE[1]):
        #   Do not delete
        await remove_boss.finish(
            message=InteractionMessage.RECORD_CHANGE_ABORT
        )
    else:
        remove_result = await boss_database.remove(state['boss_id'])
        if remove_result['status'] != DBStatusCode.DELETE_SUCCESS:
            if bot.config.debug:
                await bot.send_private_msg(
                    user_id=plugin_config.AUTHOR,
                    message=str(remove_result['error'])
                )
            await remove_boss.finish('\n'.join([
                InteractionMessage.RECORD_CHANGE_FAIL,
                InteractionMessage.ERROR_MESSAGE
            ]))
        else:
            await remove_boss.finish(
                message=InteractionMessage.RECORD_CHANGE_SUCCESS
            )


@update_boss.args_parser
async def update_boss_parser(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    state[state['_current_key']] = str(event.get_message()).strip().split(plugin_config.separator)


@update_boss.handle()
async def update_boss_first_receive(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    if raw_args:
        arg_list = raw_args.split(plugin_config.separator)
        state['new_info'] = arg_list


@update_boss.got('new_info', prompt=InteractionMessage.REQUEST_ARG)
async def update_boss_requester(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    #   Check if all 3 info are provided
    if len(state['new_info']) != 3:
        await update_boss.finish(
            message=InteractionMessage.INVALID_ARG_NUMBER
        )

    #   Check if the provided boss_id is in the records
    search_result = await boss_database.search(str(state['new_info'][0]).strip())

    if search_result['status'] != DBStatusCode.SEARCH_SUCCESS:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(search_result['error'])
            )
        await update_boss.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))
    else:
        if search_result['result']:
            #   Record found, ask for confirmation
            await update_boss.pause(
                prompt='\n'.join([
                    InteractionMessage.RECORD_FIND_SUCCESS.format(str(state['new_info'][0]).strip()),
                    InteractionMessage.REQUEST_CONFIRM
                ])
            )
        else:
            #   Record not found
            await update_boss.finish(
                message='\n'.join([
                    InteractionMessage.RECORD_FIND_FAIL.format(str(state['new_info'][0]).strip()),
                    InteractionMessage.RECORD_CHANGE_FAIL
                ])
            )


@update_boss.handle()
async def update_boss_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    #   Request valid confirmation for update
    while True:
        if str(event.get_message()).strip() not in InteractionMessage.CONFIRMATION_MESSAGE:
            await update_boss.reject(InteractionMessage.INVALID_ARG)
        else:
            break

    user_confirm = str(event.get_message()).strip()
    if user_confirm.startswith(InteractionMessage.CONFIRMATION_MESSAGE[1]):
        #   Do not update
        await update_boss.finish(
            message=InteractionMessage.RECORD_CHANGE_ABORT
        )
    else:
        new_info = {
            'id': int(str(state['new_info'][0]).strip()),
            'alias': str(state['new_info'][1]).strip(),
            'health': int(str(state['new_info'][2]).strip())
        }
        update_result = await boss_database.update(new_info)

        if update_result['status'] != DBStatusCode.UPDATE_SUCCESS:
            if bot.config.debug:
                await bot.send_private_msg(
                    user_id=plugin_config.AUTHOR,
                    message=str(update_result['error'])
                )
            await update_boss.finish('\n'.join([
                InteractionMessage.RECORD_CHANGE_FAIL,
                InteractionMessage.ERROR_MESSAGE
            ]))
        else:
            await update_boss.finish(
                message=InteractionMessage.RECORD_CHANGE_SUCCESS
            )


@search_boss.args_parser
async def search_boss_parser(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    state[state['_current_key']] = str(event.get_message()).strip()


@search_boss.handle()
async def search_boss_first_receive(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    raw_arg = str(event.get_message()).strip()
    if raw_arg:
        state['search_info'] = raw_arg


@search_boss.got('search_info', prompt=InteractionMessage.REQUEST_ARG)
async def search_boss_handler(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    search_result = await boss_database.search(str(state['search_info']).strip())

    if search_result['status'] != DBStatusCode.SEARCH_SUCCESS:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(search_result['error'])
            )
        await search_boss.finish(InteractionMessage.ERROR_MESSAGE)
    else:
        if not search_result['result']:
            #   No record found
            await search_boss.finish(InteractionMessage.RECORD_FIND_FAIL.format(state['search_info']))
        else:
            raw_info = search_result['result']

            await search_boss.finish(
                InteractionMessage.RECORD_FIND_SUCCESS.format(state['search_info'])
                + '\n\t'
                + _info_format(raw_info)
            )


@list_boss.handle()
async def list_boss_retriever(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    boss_list_result = await boss_database.display()

    if boss_list_result['status'] != DBStatusCode.SEARCH_SUCCESS:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(boss_list_result['error'])
            )
        await search_boss.finish(InteractionMessage.ERROR_MESSAGE)
    else:
        if not boss_list_result['result']:
            #   No boss stored
            await search_boss.finish(InteractionMessage.RECORD_LIST_EMPTY)
        else:
            state['boss_list'] = boss_list_result['result']

            output_message = InteractionMessage.RECORD_LIST_SUCCESS + '\n\t' + \
                             '\n\t'.join(map(_info_format, boss_list_result['result']))

            await search_boss.finish(message=output_message)


#   :param: raw_info should be {'id': id, 'alias': alias, 'health': health}
def _info_format(raw_info):
    return 'BossID: {}; '.format(str(raw_info['id'])) + \
           'Boss名: {}; '.format(raw_info['alias']) + \
           '血量: {}; '.format(str(raw_info['health']))
