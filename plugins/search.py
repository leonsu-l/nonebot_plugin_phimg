from typing import Union

from nonebot.log import logger
from nonebot.exception import FinishedException
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
    MessageSegment,
    Bot
)

from ..services.managers import group_cfg, global_cfg
from ..services.errors import NoImagesFoundError, PhilomenaAPIError

from .packer import ImagePacker, WebMPacker, ImageListPacker
from .sender import CommonSender, MergeForwardSender, MultiSegmentSender
from ..services.apis import Tags2ImgSearcher, Img2ImgSearcher

def parse_tags(tags_str: str, event: Union[MessageEvent, PrivateMessageEvent, GroupMessageEvent], onglobal: bool) -> list[str]:
    user_tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
    group_tags = group_cfg.get_tags(str(event.group_id)) if isinstance(event, GroupMessageEvent) else []
    global_tags = global_cfg.get_tags() if onglobal else []

    all_tags = group_tags + global_tags + user_tags
    return list(set(all_tags)) # 去重

async def handle_search(
    cmd,
    event: GroupMessageEvent,
    onglobal: bool,
    bot: Bot,
    search_query: dict
):
    try:
        mode: str = search_query['mode']
        if mode == 'tags2img':
            tags_str = search_query.get("tags", "")
            tags_list = parse_tags(tags_str, event, onglobal)
            logger.info(f"搜索所用tags: {tags_list}")

            query_params = {
                "q": ','.join(tags_list),
                "key": global_cfg.get_key(),
                'per_page': 50,
                'page': 1,
                'sf': "score",
                'sd': "desc",
            }
            searcher = Tags2ImgSearcher(query_params)
            selected_img = await searcher.select_img()
            file_type = selected_img['view_url'].split('.')[-1].lower()
            logger.info(f"选中图片类型: {file_type}")

            if file_type in ['webm', 'mp4']:
                packer = WebMPacker(selected_img)
                packet = packer.get_packet()
                sender = MergeForwardSender(bot, event.user_id, event.group_id)
                sender.msg = (packet, query_params["q"])
                await sender.send()
            else:
                packer = ImagePacker(selected_img)
                packet = packer.get_packet()
                sender = CommonSender(bot, event.user_id, event.group_id)
                sender.msg = (packet, query_params["q"])
                await sender.send()
                
        elif mode == 'img2img':
            query_params = {
                "key": global_cfg.get_key(),
                "url": search_query.get("url", ""),
                "distance": search_query.get("distance", "0.25"),
            }
            searcher = Img2ImgSearcher(query_params)
            selected_img_list = await searcher.select_img_list()
            packer = ImageListPacker(selected_img_list)
            packet = packer.get_packet()
            sender = MultiSegmentSender(bot, event.user_id, event.group_id)
            sender.add_messages(packet)
            await sender.send()

    except NoImagesFoundError as e:
        logger.error(f"无图片: {str(e)}")
        await cmd.finish( str(e) )
    except PhilomenaAPIError as e:
        logger.error(f"Philomena API 错误: {str(e)}")
        await cmd.finish("网络错误，请联系bot管理员")
    except FinishedException as e:
        raise
    except Exception as e:
        logger.error(f"Search执行异常: {str(e)}")
        raise