from typing import Union

from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
    GroupMessageEvent,
    Message
)
from nonebot import get_driver, on_command
from nonebot.params import CommandArg
from nonebot.log import logger
from nonebot.permission import SUPERUSER

from .search import tags_search_img
from ..utils import group_only

driver = get_driver()
driver.config.command_start = {".", "。"}

request = on_command("搜图")

@request.handle()
async def _(
    event: Union[MessageEvent, PrivateMessageEvent, GroupMessageEvent],
    arg: Message = CommandArg()
):
    arg_str = arg.extract_plain_text().strip()
    # if isinstance(event, GroupMessageEvent):
    #     if event.user_id == SUPERUSER or event.sender.role in ["owner", "admin"]:
    #         logger.info(f"指令为{arg_str}")
    #         if arg_str == "on":
    #             group_cfg.enable(str(event.group_id))
    #             await request.finish("已在本群开启搜图")
    #         elif arg_str == "off":
    #             group_cfg.disable(str(event.group_id))
    #             await request.finish("已在本群关闭搜图")
    #         else:
    #             await request.finish("未知指令")
    #     if not group_cfg.get_status(str(event.group_id)):
    #         await request.finish("功能未在本群开启，管理员请用 。搜图 on 启动")

    at_user = MessageSegment.at(event.user_id)

    img_info = await get_img_info(arg_str, at_user)
    logger.success(f"图片信息: {img_info}")

    img_url = img_info["url"]
    img_score = img_info["score"]
    # image = MessageSegment.image(img_url) if img_url else None
    img_id = img_url.split('/')[-2] if img_url else None
    await request.send(at_user + '''image''' + f"id: {img_id}\nscore: {img_score}")
    await request.finish()

async def get_img_info(arg_str: str, at_user: MessageSegment) -> dict:
    try:
        img_info = await tags_search_img(arg_str)
    except FileNotFoundError:
        await request.finish(at_user + " 没有找到相关图片")
    except Exception as e:
        await request.finish(at_user + f" bot异常: {str(e)}")
    if not img_info:
        await request.finish(at_user + " bot因未知原因未能找到图片，请联系管理员")
    return img_info