from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name = "EQAD Derpibooru图片搜索",
    description = "从Derpibooru搜索图片",
    usage = ".搜图 [tags/on/off]",
    type = "application"
)

from .plugins import cmd_handler