from nonebot.plugin import PluginMetadata
from nonebot import get_driver

from .utils import init

__plugin_meta__ = PluginMetadata(
    name = "EQAD Derpibooru图片搜索",
    description = "从Derpibooru搜索图片",
    usage = ".搜图 [tags/on/off]",
    type = "application"
)

driver = get_driver()

@driver.on_startup
async def _():
    """NoneBot2 启动时初始化配置加载模块"""
    await init()
    
from .plugins import cmd_handler