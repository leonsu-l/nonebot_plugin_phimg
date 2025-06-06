from random import randint
from typing import Union

from nonebot.log import logger

from .apis import tags_search_img

async def _(
    tags_str: str, 
    per_page: int = 50, 
    **kwargs
) -> dict[str, Union[str, int]]:
    """根据tags搜图"""
    tags_list = parse_tags(tags_str)
    imgs_list = await tags_search_img(tags_list, per_page, **kwargs)
    return select_random_img(imgs_list)

def parse_tags(tags_str: str) -> list:
    """将传入的tags字符串转换为列表"""
    tags_list = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
    logger.info(f"搜索标签为：{tags_list}")
    return tags_list

def select_random_img(imgs_list: list[dict]) -> dict:
    """已有列表中随机选一个图片"""
    img_index = randint(0, len(imgs_list) - 1)
    selected_img = imgs_list[img_index]

    return {
        "url": selected_img["representations"]["large"],
        "score": selected_img["score"]
    }