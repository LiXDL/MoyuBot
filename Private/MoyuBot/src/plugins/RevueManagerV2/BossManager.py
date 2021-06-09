import asyncio

import nonebot
import nonebot.typing as typing
import nonebot.permission as permission
import nonebot.adapters.cqhttp as cqhttp
import nonebot.adapters.cqhttp.permission as cpermission

from nonebot.plugin import on_command

from .config import Config
from .constants import InteractionMessage
from . import data_source

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

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

delete_boss = on_command(
    cmd='delete_boss',
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

add_boss_range = on_command(
    cmd='add_boss_range',
    aliases={'添加boss组', 'abr'},
    permission=permission.SUPERUSER | cpermission.GROUP_OWNER | cpermission.GROUP_ADMIN,
    priority=1
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
        'boss_id': int(str(state['info'][0]).strip()),
        'alias': str(state['info'][1]).strip(),
        'health': int(str(state['info'][2]).strip())
    }

    add_result = await data_source.bc.add(info)
    if add_result['error'] is None:
        await add_boss.finish(InteractionMessage.RECORD_CHANGE_SUCCESS)
    else:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=add_result['func_info']
            )
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=add_result['error']
            )
        await add_boss.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))


@delete_boss.args_parser
async def delete_boss_parser(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    state[state['_current_key']] = int(str(event.get_message()).strip())


@delete_boss.handle()
async def delete_boss_first_receive(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    if raw_args:
        state['boss_id'] = int(raw_args)


@delete_boss.got('boss_id', prompt=InteractionMessage.REQUEST_ARG)
async def delete_boss_requester(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    #   Check if the provided boss_id is in the records
    search_result = await data_source.bc.search(state['boss_id'])

    if search_result['error'] is not None:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=search_result['func_info']
            )
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=search_result['error']
            )
        await delete_boss.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))
    else:
        if search_result['response']['result']:
            #   Record found, ask for confirmation
            await delete_boss.pause(
                prompt='\n'.join([
                    InteractionMessage.RECORD_FIND_SUCCESS.format(state['boss_id']),
                    InteractionMessage.REQUEST_CONFIRM
                ])
            )
        else:
            #   Record not found
            await delete_boss.finish(
                message='\n'.join([
                    InteractionMessage.RECORD_FIND_FAIL.format(state['boss_id']),
                    InteractionMessage.RECORD_CHANGE_FAIL
                ])
            )


@delete_boss.handle()
async def delete_boss_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    #   Request valid confirmation for deletion
    while True:
        if str(event.get_message()).strip() not in InteractionMessage.CONFIRMATION_MESSAGE:
            await delete_boss.reject(InteractionMessage.INVALID_ARG)
        else:
            break

    user_confirm = str(event.get_message()).strip()
    if user_confirm.startswith(InteractionMessage.CONFIRMATION_MESSAGE[1]):
        #   Do not delete
        await delete_boss.finish(message=InteractionMessage.RECORD_CHANGE_ABORT)
    else:
        delete_result = await data_source.bc.delete(state['boss_id'])
        if delete_result['error'] is None:
            await delete_boss.finish(message=InteractionMessage.RECORD_CHANGE_SUCCESS)
        else:
            if bot.config.debug:
                await bot.send_private_msg(
                    user_id=plugin_config.AUTHOR,
                    message=delete_result['func_info']
                )
                await bot.send_private_msg(
                    user_id=plugin_config.AUTHOR,
                    message=delete_result['error']
                )
            await delete_boss.finish('\n'.join([
                InteractionMessage.RECORD_CHANGE_FAIL,
                InteractionMessage.ERROR_MESSAGE
            ]))


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
    search_result = await data_source.bc.search(str(state['new_info'][0]).strip())

    if search_result['error'] is not None:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=search_result['func_info']
            )
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=search_result['error']
            )
        await update_boss.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))
    else:
        if search_result['response']['result']:
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
        await update_boss.finish(message=InteractionMessage.RECORD_CHANGE_ABORT)
    else:
        new_info = {
            'boss_id': int(str(state['new_info'][0]).strip()),
            'alias': str(state['new_info'][1]).strip(),
            'health': int(str(state['new_info'][2]).strip())
        }
        update_result = await data_source.bc.update(new_info)

        if update_result['error'] is not None:
            await update_boss.finish(message=InteractionMessage.RECORD_CHANGE_SUCCESS)
        else:
            if bot.config.debug:
                await bot.send_private_msg(
                    user_id=plugin_config.AUTHOR,
                    message=update_result['func_info']
                )
                await bot.send_private_msg(
                    user_id=plugin_config.AUTHOR,
                    message=update_result['error']
                )
            await update_boss.finish('\n'.join([
                InteractionMessage.RECORD_CHANGE_FAIL,
                InteractionMessage.ERROR_MESSAGE
            ]))


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
    search_result = await data_source.bc.search(str(state['search_info']).strip())

    if search_result['error'] is not None:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=search_result['func_tool']
            )
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=search_result['error']
            )
        await search_boss.finish(InteractionMessage.ERROR_MESSAGE)
    else:
        if not search_result['response']['result']:
            #   No record found
            await search_boss.finish(InteractionMessage.RECORD_FIND_FAIL.format(state['search_info']))
        else:
            raw_info = search_result['response']['result']

            await search_boss.finish(
                InteractionMessage.RECORD_FIND_SUCCESS.format(state['search_info'])
                + '\n\t'
                + _info_format(raw_info)
            )


@list_boss.handle()
async def list_boss_retriever(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    boss_list_result = await data_source.bc.list()

    if boss_list_result['error'] is not None:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=boss_list_result['func_info']
            )
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=boss_list_result['error']
            )
        await search_boss.finish(InteractionMessage.ERROR_MESSAGE)
    else:
        if not boss_list_result['response']['result']:
            #   No boss stored
            await search_boss.finish(InteractionMessage.RECORD_LIST_EMPTY)
        else:
            await search_boss.finish(
                InteractionMessage.RECORD_LIST_SUCCESS
                + '\n\t'
                + '\n\t'.join(map(_info_format, boss_list_result['response']['result']))
            )


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

    adding_tasks = []

    for level in range(start_level, end_level):
        for i in range(len(boss_names)):
            info = {
                'boss_id': level * 100 + i + 1,
                'alias': 'R' + str(level) + boss_names[i],
                'health': boss_healths[i]
            }
            adding_tasks.append(asyncio.create_task(data_source.bc.add(info)))

    await asyncio.wait(adding_tasks)

    await add_boss_range.finish(
        message='Added Boss in level range {} and {}'.format(start_level, end_level)
    )


#   :param: raw_info should be {'boss_id': id, 'alias': alias, 'health': health}
def _info_format(raw_info):
    return 'BossID: {}; '.format(str(raw_info['boss_id'])) + \
           'Boss名: {}; '.format(raw_info['alias']) + \
           '血量: {}; '.format(str(raw_info['health']))