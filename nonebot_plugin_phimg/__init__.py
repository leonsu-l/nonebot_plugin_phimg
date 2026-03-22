from nonebot.plugin import PluginMetadata
from nonebot import get_driver, logger

from .services.managers import init

__plugin_meta__ = PluginMetadata(
    name = "EQAD Philomena图片搜索",
    description = "从Philomena系图站搜索图片",
    usage = ".搜图 [tags/on/off]",
    type = "application"
)

driver = get_driver()

@driver.on_startup
async def _():
    """NoneBot2 启动时初始化配置加载模块"""
    await init()
    
from . import cmd_handler

__all__ = ["cmd_handler"]