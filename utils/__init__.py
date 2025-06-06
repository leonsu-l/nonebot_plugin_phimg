from nonebot.matcher import Matcher
from nonebot.params import RawCommand

async def group_only(matcher: Matcher, command: str = RawCommand()):
    await matcher.finish(f"只有群里才能{command}")

from .config_manager import group_cfg, global_cfg