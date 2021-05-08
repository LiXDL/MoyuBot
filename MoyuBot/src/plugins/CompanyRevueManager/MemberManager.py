from pathlib import Path

import nonebot
import nonebot.typing as typing
import nonebot.plugin as plugin
import nonebot.permission as permission
import nonebot.adapters.cqhttp as cqhttp
import nonebot.adapters.cqhttp.permission as c_permission
from .config import Config

import MemberDB

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())


member_database = MemberDB.MemberDB(Path().cwd().joinpath('CompanyRevue.db'))

add_member = plugin.on_command(
    ('add_member', '添加成员'),
    permission=permission.SUPERUSER | c_permission.GROUP_OWNER | c_permission.GROUP_ADMIN,
    priority=1
)

remove_member = plugin.on_command(
    ('remove_member', '移除成员'),
    permission=permission.SUPERUSER | c_permission.GROUP_OWNER | c_permission.GROUP_ADMIN,
    priority=2
)

update_member = plugin.on_command(
    ('update_member', '更新成员'),
    permission=permission.SUPERUSER | c_permission.GROUP_OWNER | c_permission.GROUP_ADMIN,
    priority=3
)

search_member = plugin.on_command(
    ('search_member', '搜索成员'),
    priority=4
)

list_member = plugin.on_command(
    ('list_member', '成员列表'),
    priority=4
)


@add_member.handle()
async def add_member_handler(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
    args = str(event.get_message()).strip()

