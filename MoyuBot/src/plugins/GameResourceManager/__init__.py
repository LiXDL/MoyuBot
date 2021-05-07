import nonebot
from nonebot import permission
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
from .config import Config


global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())

