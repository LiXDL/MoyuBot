from pathlib import Path

import nonebot
import nonebot.typing as typing
import nonebot.permission as permission
import nonebot.adapters.cqhttp as cqhttp

from nonebot.plugin import on_command

from .config import Config
from .model import InteractionMessage, DBStatusCode
from . import MemberDB

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

member_database = MemberDB.MemberDB(
    Path().cwd()
    .joinpath(plugin_config.company_storage)
    .joinpath(plugin_config.company_record)
    .joinpath('CompanyRevue.db')
)

helper = on_command(
    cmd='help_member',
    aliases={'成员管理'},
    priority=10
)

add_member = on_command(
    cmd='add_member',
    aliases={'添加成员'},
    permission=permission.SUPERUSER,
    priority=1
)

remove_member = on_command(
    cmd='remove_member',
    aliases={'移除成员'},
    permission=permission.SUPERUSER,
    priority=2
)

update_member = on_command(
    cmd='update_member',
    aliases={'更新成员'},
    permission=permission.SUPERUSER,
    priority=3
)

search_member = on_command(
    cmd='search_member',
    aliases={'搜索成员'},
    priority=4
)

list_member = on_command(
    cmd='list_member',
    aliases={'成员列表'},
    priority=4
)


@helper.handle()
async def helper_handler(bot: cqhttp.Bot, event: cqhttp.Event):
    await helper.finish(InteractionMessage.MEMBER_MANAGER_HELP_MESSAGE)


@add_member.args_parser
async def add_member_parser(bot: cqhttp.Bot, event: cqhttp.PrivateMessageEvent, state: typing.T_State):
    state[state['_current_key']] = str(event.get_message()).strip().split(plugin_config.separator)


@add_member.handle()
async def add_member_first_receive(bot: cqhttp.Bot, event: cqhttp.PrivateMessageEvent, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    if raw_args:
        arg_list = raw_args.split(plugin_config.separator)
        state['info'] = arg_list


@add_member.got('info', prompt=InteractionMessage.REQUEST_ARG)
async def add_member_handler(bot: cqhttp.Bot, event: cqhttp.PrivateMessageEvent, state: typing.T_State):
    #   Check if all 4 info are provided
    if len(state['info']) != 4:
        await add_member.finish(
            message=InteractionMessage.INVALID_ARG_NUMBER
        )

    info = {
        'id': str(state['info'][0]).strip(),
        'alias': str(state['info'][1]).strip(),
        'account': str(state['info'][2]).strip(),
        'password': str(state['info'][3]).strip()
    }

    add_result = await member_database.add(info)
    if add_result['status'] == DBStatusCode.INSERT_SUCCESS:
        await add_member.finish(InteractionMessage.RECORD_CHANGE_SUCCESS)
    else:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(add_result['error']))

        await add_member.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))


@remove_member.args_parser
async def remove_member_parser(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    state[state['_current_key']] = str(event.get_message()).strip()


@remove_member.handle()
async def remove_member_first_receive(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    if raw_args:
        state['member_id'] = raw_args


@remove_member.got('member_id', prompt=InteractionMessage.REQUEST_ARG)
async def remove_member_requester(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    #   Check if the provided member_id is in the records
    search_result = await member_database.search(state['member_id'])

    if search_result['status'] != DBStatusCode.SEARCH_SUCCESS:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(search_result['error'])
            )
        await remove_member.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))
    else:
        if search_result['result']:
            #   Record found, ask for confirmation
            await remove_member.pause(
                prompt='\n'.join([
                    InteractionMessage.RECORD_FIND_SUCCESS.format(state['member_id']),
                    InteractionMessage.REQUEST_CONFIRM
                ])
            )
        else:
            #   Record not found
            await remove_member.finish(
                message='\n'.join([
                    InteractionMessage.RECORD_FIND_FAIL.format(state['member_id']),
                    InteractionMessage.RECORD_CHANGE_FAIL
                ])
            )


@remove_member.handle()
async def remove_member_handler(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    #   Request valid confirmation for deletion
    while True:
        if str(event.get_message()).strip() not in InteractionMessage.CONFIRMATION_MESSAGE:
            await remove_member.reject(InteractionMessage.INVALID_ARG)
        else:
            break

    user_confirm = str(event.get_message()).strip()
    if user_confirm.startswith(InteractionMessage.CONFIRMATION_MESSAGE[1]):
        #   Do not delete
        await remove_member.finish(
            message=InteractionMessage.RECORD_CHANGE_ABORT
        )
    else:
        remove_result = await member_database.remove(state['member_id'])
        if remove_result['status'] != DBStatusCode.DELETE_SUCCESS:
            if bot.config.debug:
                await bot.send_private_msg(
                    user_id=plugin_config.AUTHOR,
                    message=str(remove_result['error'])
                )
            await remove_member.finish('\n'.join([
                InteractionMessage.RECORD_CHANGE_FAIL,
                InteractionMessage.ERROR_MESSAGE
            ]))
        else:
            await remove_member.finish(
                message=InteractionMessage.RECORD_CHANGE_SUCCESS
            )


@update_member.args_parser
async def update_member_parser(bot: cqhttp.Bot, event: cqhttp.PrivateMessageEvent, state: typing.T_State):
    state[state['_current_key']] = str(event.get_message()).strip().split(plugin_config.separator)


@update_member.handle()
async def update_member_first_receive(bot: cqhttp.Bot, event: cqhttp.PrivateMessageEvent, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    if raw_args:
        arg_list = raw_args.split(plugin_config.separator)
        state['new_info'] = arg_list


@update_member.got('new_info', prompt=InteractionMessage.REQUEST_ARG)
async def update_member_requester(bot: cqhttp.Bot, event: cqhttp.PrivateMessageEvent, state: typing.T_State):
    #   Check if all 4 info are provided
    if len(state['new_info']) != 4:
        await update_member.finish(
            message=InteractionMessage.INVALID_ARG_NUMBER
        )

    #   Check if the provided member_id is in the records
    search_result = await member_database.search(str(state['new_info'][0]).strip())

    if search_result['status'] != DBStatusCode.SEARCH_SUCCESS:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(search_result['error'])
            )
        await update_member.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))
    else:
        if search_result['result']:
            #   Record found, ask for confirmation
            await update_member.pause(
                prompt='\n'.join([
                    InteractionMessage.RECORD_FIND_SUCCESS.format(str(state['new_info'][0]).strip()),
                    InteractionMessage.REQUEST_CONFIRM
                ])
            )
        else:
            #   Record not found
            await update_member.finish(
                message='\n'.join([
                    InteractionMessage.RECORD_FIND_FAIL.format(str(state['new_info'][0]).strip()),
                    InteractionMessage.RECORD_CHANGE_FAIL
                ])
            )


@update_member.handle()
async def update_member_handler(bot: cqhttp.Bot, event: cqhttp.PrivateMessageEvent, state: typing.T_State):
    #   Request valid confirmation for update
    while True:
        if str(event.get_message()).strip() not in InteractionMessage.CONFIRMATION_MESSAGE:
            await update_member.reject(InteractionMessage.INVALID_ARG)
        else:
            break

    user_confirm = str(event.get_message()).strip()
    if user_confirm.startswith(InteractionMessage.CONFIRMATION_MESSAGE[1]):
        #   Do not update
        await update_member.finish(
            message=InteractionMessage.RECORD_CHANGE_ABORT
        )
    else:
        new_info = {
            'id': str(state['new_info'][0]).strip(),
            'alias': str(state['new_info'][1]).strip(),
            'account': str(state['new_info'][2]).strip(),
            'password': str(state['new_info'][3]).strip()
        }
        update_result = await member_database.update(new_info)

        if update_result['status'] != DBStatusCode.UPDATE_SUCCESS:
            if bot.config.debug:
                await bot.send_private_msg(
                    user_id=plugin_config.AUTHOR,
                    message=str(update_result['error'])
                )
            await update_member.finish('\n'.join([
                InteractionMessage.RECORD_CHANGE_FAIL,
                InteractionMessage.ERROR_MESSAGE
            ]))
        else:
            await update_member.finish(
                message=InteractionMessage.RECORD_CHANGE_SUCCESS
            )


@search_member.args_parser
async def search_member_parser(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    state[state['_current_key']] = str(event.get_message()).strip()


@search_member.handle()
async def search_member_first_receive(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    raw_arg = str(event.get_message()).strip()
    if raw_arg:
        state['search_info'] = raw_arg


@search_member.got('search_info', prompt=InteractionMessage.REQUEST_ARG)
async def search_member_searcher(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    search_result = await member_database.search(str(state['search_info']).strip())

    if search_result['status'] != DBStatusCode.SEARCH_SUCCESS:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(search_result['error'])
            )
        await search_member.finish(InteractionMessage.ERROR_MESSAGE)
    else:
        if not search_result['result']:
            #   No record found
            await search_member.finish(InteractionMessage.RECORD_FIND_FAIL.format(state['search_info']))
        else:
            state['search_result'] = search_result


@search_member.handle()
async def search_member_private_handler(bot: cqhttp.Bot, event: cqhttp.PrivateMessageEvent, state: typing.T_State):
    raw_info = state['search_result']['result']

    if event.user_id in plugin_config.ADMIN:
        #   Output full information for Company Administrator
        await search_member.finish(
            InteractionMessage.RECORD_FIND_SUCCESS.format(state['search_info']) + '\n' +
            '\t' + _admin_info_format(raw_info)
        )
    else:
        #   Output only non-private information for ordinary member
        await search_member.finish(
            InteractionMessage.RECORD_FIND_SUCCESS.format(state['search_info']) + '\n' +
            '\t' + _non_admin_info_format(raw_info)
        )


@search_member.handle()
async def search_member_group_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    raw_info = state['search_result']['result']

    if event.sender.role in ['owner', 'admin'] or event.user_id in plugin_config.ADMIN:
        #   Output full information for Company Administrator through private message
        await bot.send_private_msg(
            user_id=event.user_id,
            message=InteractionMessage.RECORD_FIND_SUCCESS.format(state['search_info']) + '\n' +
            '\t' + _admin_info_format(raw_info)
        )
        await search_member.finish(
            message=InteractionMessage.PRIVATE_MESSAGE_SENT_CHECK,
            at_sender=True
        )
    else:
        #   Output only non-private information for ordinary member
        await search_member.finish(
            message=InteractionMessage.RECORD_FIND_SUCCESS.format(state['search_info']) + '\n' +
            '\t' + _non_admin_info_format(raw_info)
        )


@list_member.handle()
async def list_member_retriever(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    member_list_result = await member_database.display()

    if member_list_result['status'] != DBStatusCode.SEARCH_SUCCESS:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=str(member_list_result['error'])
            )
        await search_member.finish(InteractionMessage.ERROR_MESSAGE)
    else:
        if not member_list_result['result']:
            #   No member stored
            await search_member.finish(InteractionMessage.RECORD_LIST_EMPTY)
        else:
            state['member_list'] = member_list_result['result']


@list_member.handle()
async def list_member_private_handler(bot: cqhttp.Bot, event: cqhttp.PrivateMessageEvent, state: typing.T_State):
    if event.user_id in plugin_config.ADMIN:
        #   Output full information for Company Administrator
        output_message = InteractionMessage.RECORD_LIST_SUCCESS + '\n\t' + \
                         '\n\t'.join(map(_admin_info_format, state['member_list']))

        await search_member.finish(message=output_message)
    else:
        #   Output only non-private information for ordinary member
        output_message = InteractionMessage.RECORD_LIST_SUCCESS + '\n\t' + \
                         '\n\t'.join(map(_non_admin_info_format, state['member_list']))

        await search_member.finish(message=output_message)


@list_member.handle()
async def list_member_group_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    if event.sender.role in ['owner', 'admin'] or event.user_id in plugin_config.ADMIN:
        #   Output full information for Company Administrator through private message
        output_message = InteractionMessage.RECORD_LIST_SUCCESS + '\n\t' + \
                         '\n\t'.join(map(_admin_info_format, state['member_list']))

        await bot.send_private_msg(
            user_id=event.user_id,
            message=output_message
        )
        await search_member.finish(
            message=InteractionMessage.PRIVATE_MESSAGE_SENT_CHECK,
            at_sender=True
        )
    else:
        #   Output only non-private information for ordinary member
        output_message = InteractionMessage.RECORD_LIST_SUCCESS + '\n\t' + \
                         '\n\t'.join(map(_non_admin_info_format, state['member_list']))

        await search_member.finish(message=output_message)


#   :param: raw_info should be {'id': id, 'alias': alias, 'account': account, 'password': password}
def _admin_info_format(raw_info: dict):
    return 'QQ号: {}; '.format(raw_info['id']) + \
           '昵称: {}; '.format(raw_info['alias']) + \
           '账号: {}; '.format(raw_info['account']) + \
           '密码: {}.'.format(raw_info['password'])


#   :param: raw_info should be {'id': id, 'alias': alias, 'account': account, 'password': password}
def _non_admin_info_format(raw_info: dict):
    return 'QQ号: {}; '.format(raw_info['id']) + \
           '昵称: {}. '.format(raw_info['alias'])
