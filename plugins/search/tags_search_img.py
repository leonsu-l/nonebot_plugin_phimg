from random import randint

from .apis import tags_search_img

async def _(
    tags_list: list[str], 
    key: str,
    **kwargs
) -> dict:
    """根据tags搜图"""
    imgs_list = await tags_search_img(tags_list, key=key, **kwargs)
    return select_random_img(imgs_list)

def select_random_img(imgs_list: list[dict]) -> dict:
    """已有列表中随机选一个图片"""
    img_index = randint(0, len(imgs_list) - 1)
    selected_img = imgs_list[img_index]

    return {
        "url": selected_img["representations"]["large"],
        "score": selected_img["score"]
    }