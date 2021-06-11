from pathlib import Path

import nonebot
import nonebot.typing as typing
import nonebot.permission as permission
import nonebot.adapters.cqhttp as cqhttp

from .constants import InteractionMessage
from . import data_source
from . import MemberManager, BossManager, RecordManager, TeamManager

from nonebot.plugin import on_command


bot_driver = nonebot.get_driver()

bot_driver.on_startup(
    lambda: data_source.init_database(str(
        Path.cwd().joinpath('Data/Company').joinpath('ORMTest').joinpath('Revue.db')
    ))
)

# test_message_helper = on_command('test_message', aliases={'tm'}, priority=10)

overall_helper = on_command(
    cmd='help',
    aliases={'帮助'},
    priority=10
)

clear_db = on_command(
    cmd='EMPTY',
    permission=permission.SUPERUSER,
    priority=1
)


@overall_helper.handle()
async def helper_handler(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    await overall_helper.finish(InteractionMessage.OVERALL_HELPER)


@clear_db.handle()
async def clearance(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    db_file = Path.cwd().joinpath('Data/Company').joinpath('ORMTest').joinpath('Revue.db')

    await data_source.reset_database(str(db_file))
    await clear_db.finish('Cleared database at: {}'.format(str(db_file)))


# @test_message_helper.handle()
# async def message_helper(bot: cqhttp.Bot, event: cqhttp.GroupMessageEvent, state: typing.T_State):
#     pass
#     message = event.get_message()
#     print(message)
#     if message is None:
#         await test_message_helper.finish('Empty Message')
#     else:
#         result = ''
#         for segment in message:
#             result = result +
#             'Current segment: type [{}], content [{}]\n'.format(type(segment), str(segment.__dict__))
#
#         await test_message_helper.send(message=str(len(message)))
#         await test_message_helper.finish(result)
