import nonebot
import nonebot.typing as typing
import nonebot.permission as permission
import nonebot.adapters.cqhttp as cqhttp
import nonebot.adapters.cqhttp.permission as cpermission

from nonebot.plugin import on_command

from .config import Config
from .constants import InteractionMessage
from . import data_source as ds

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

helper = on_command(
    cmd='helper_team',
    aliases={'队伍管理'},
    priority=10
)

add_team = on_command(
    cmd='add_team',
    aliases={'添加队伍', 'at'},
    priority=1
)

remove_team = on_command(
    cmd='remove_team',
    aliases={'删除队伍', 'rt'},
    permission=permission.SUPERUSER | cpermission.GROUP_OWNER | cpermission.GROUP_ADMIN,
    priority=2
)

search_team = on_command(
    cmd='search_team',
    aliases={'查询队伍', 'st'},
    priority=10
)


@helper.handle()
async def helper_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    await helper.finish(InteractionMessage.TEAM_MANAGER_HELPER_MESSAGE)


@add_team.handle()
async def add_team_first_receive(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    raw_message = event.get_message()
    arg_list, prior_id = None, None

    if len(raw_message) != 0:
        for segment in raw_message:
            if segment['type'] == 'at':
                #   checking for @message and extract qq_id from it as member_id
                prior_id = segment['data']['qq']
            else:
                arg_list = list(map(
                    lambda x: str(x).strip(),
                    str(segment['data']['text']).strip().split(plugin_config.separator)
                ))

                if len(arg_list) < 1 or len(arg_list) > 2:
                    await add_team.finish(InteractionMessage.INVALID_ARG)
                elif len(arg_list) == 2:
                    state['member_id'] = arg_list[1]
    else:
        await add_team.reject(prompt=InteractionMessage.REQUEST_ARG)

    state['member_id'] = prior_id if (prior_id is not None) else (
        state.get('member_id', event.user_id)
    )
    state['team_id'] = int(arg_list[0])

    #   check if there is already a team belongs to the given member
    team_existence = await ds.tc.search_team(state['member_id'], state['team_id'])
    if team_existence['response']['result']:
        await add_team.finish(InteractionMessage.RECORD_ALREADT_EXIST)
    else:
        state['team_list'] = []
        state['us_list'] = []
        await add_team.pause(
            prompt=InteractionMessage.REPEATE_ADD_TEAM_CARD
        )


@add_team.handle()
async def add_team_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    while True:
        action = str(event.get_message()).strip()
        if action == 'confirm':
            if not state['team_list']:
                await add_team.reject(prompt=InteractionMessage.NOT_ENOUGH_TEAM)
            else:
                break
        elif action == 'abort':
            await add_team.finish(InteractionMessage.RECORD_CHANGE_ABORT)
        else:
            card = action.split(plugin_config.separator)
            if len(card) != 2:
                await add_team.reject(prompt=InteractionMessage.INVALID_ARG_NUMBER)
            else:
                state['team_list'].append(card[0])
                state['us_list'].append(card[1])
                await add_team.reject(prompt=InteractionMessage.REPEATE_ADD_TEAM_CARD)

    team_info = {
        'member_id': state['member_id'],
        'team_id': state['team_id'],
        'team_list': ','.join(state['team_list']),
        'us_list': ','.join(state['us_list'])
    }
    print(team_info)

    add_result = await ds.tc.add(team_info)
    print(add_result)
    if add_result['error'] is None:
        await add_team.finish(InteractionMessage.RECORD_CHANGE_SUCCESS)
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
        await add_team.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))


@remove_team.handle()
async def remove_team_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    raw_args = str(event.get_message()).strip()
    arg_list = list(map(str.strip, raw_args.split(plugin_config.separator)))

    remove_identifier = {
        'member_id': arg_list[0]
    }
    try:
        remove_identifier['team_id'] = int(arg_list[1])
    except ValueError:
        await remove_team.finish(InteractionMessage.INVALID_ARG)

    remove_result = await ds.tc.delete(**remove_identifier)
    if remove_result['error'] is None:
        await remove_team.finish(InteractionMessage.RECORD_CHANGE_SUCCESS)
    else:
        if bot.config.debug:
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=remove_result['func_info']
            )
            await bot.send_private_msg(
                user_id=plugin_config.AUTHOR,
                message=remove_result['error']
            )
        await remove_team.finish('\n'.join([
            InteractionMessage.RECORD_CHANGE_FAIL,
            InteractionMessage.ERROR_MESSAGE
        ]))


@search_team.handle()
async def search_boss_first_receive(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    raw_message = event.get_message()
    arg_list, prior_id = None, None

    if len(raw_message) != 0:
        for segment in raw_message:
            if segment['type'] == 'at':
                #   checking for @message and extract qq_id from it as member_id
                prior_id = segment['data']['qq']
            else:
                arg_list = list(map(
                    lambda x: str(x).strip(),
                    str(segment['data']['text']).strip().split(plugin_config.separator)
                ))

                if len(arg_list) < 1 or len(arg_list) > 2:
                    await add_team.finish(InteractionMessage.INVALID_ARG)
                elif len(arg_list) == 2:
                    state['team_id'] = arg_list[1]

        state['member_id'] = arg_list[0]

    state['member_id'] = prior_id if (prior_id is not None) else (
        state.get('member_id', event.user_id)
    )


@search_team.handle()
async def search_boss_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    if state.get('team_id') is None:
        #   search for all teams belonging to a member
        search_result = await ds.tc.search_member(state.get('member_id'))
    else:
        #   search for given member_id and team_id
        search_result = await ds.tc.search_team(state.get('member_id'), state.get('team_id'))

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
        await search_team.finish(InteractionMessage.ERROR_MESSAGE)
    else:
        teams = search_result['response']['result']
        if not teams:
            await search_team.finish(InteractionMessage.RECORD_LIST_EMPTY)

        if type(teams) is dict:
            await search_team.finish(
                message=InteractionMessage.RECORD_FIND_SUCCESS.format(state.get('member_id')) + '\n' +
                InteractionMessage.RECORD_LIST_SUCCESS + '\n' + _info_format(teams)
            )
        else:
            team_records = '\n'.join(map(_info_format, teams))
            await search_team.finish(
                message=InteractionMessage.RECORD_FIND_SUCCESS.format(state.get('member_id')) + '\n' +
                InteractionMessage.RECORD_LIST_SUCCESS + '\n' + team_records
            )


def _info_format(raw_info: dict):
    return '\tQQ号: {}; 队伍序号: {};\n'.format(raw_info['member_id'], raw_info['team_id']) + \
           '\t队伍卡组: {}\n'.format(raw_info['team_list']) + \
           '\t队伍us: {}'.format(raw_info['us_list'])
