import nonebot
import nonebot.typing as typing
import nonebot.adapters.cqhttp as cqhttp

from nonebot.plugin import on_command

from . import MemberManager
from . import BossManager
from . import RevueRecordManager
from .constants import InteractionMessage

bot_driver = nonebot.get_driver()


bot_driver.on_startup(
    lambda: print('Your bot has just started.')
)

overall_helper = on_command(
    cmd='help',
    aliases={'帮助'},
    priority=10
)


@overall_helper.handle()
async def helper_handler(bot: cqhttp.Bot, event: cqhttp.Event, state: typing.T_State):
    await overall_helper.finish(InteractionMessage.OVERALL_HELPER)
