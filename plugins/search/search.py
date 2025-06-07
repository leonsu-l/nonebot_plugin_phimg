from typing import Union

from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
    MessageSegment,
)

from . import tags_search_img
# from ..handler import handle_exceptions

# @handle_exceptions
async def _(
    cmd,
    event: Union[MessageEvent, PrivateMessageEvent, GroupMessageEvent],
    tags_str: str
):
    """处理搜图命令"""
    tags_list = parse_tags(tags_str)

    img_info = await tags_search_img(tags_list)
    # img_info = await get_img_info(arg_str, at_user)
    logger.success(f"图片信息: {img_info}")

    img_url = img_info["url"]
    img_score = img_info["score"]
    # image = MessageSegment.image(img_url) if img_url else None
    img_id = img_url.split('/')[-2] if img_url else None

    at_user = MessageSegment.at(event.user_id)
    await cmd.send(at_user + '''image''' + f"id: {img_id}\nscore: {img_score}")
    await cmd.finish()

def parse_tags(tags_str: str) -> list:
    """将传入的tags字符串转换为列表"""
    tags_list = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
    logger.info(f"搜索标签为：{tags_list}")
    return tags_list
