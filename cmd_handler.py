from typing import Union
import shlex

from nonebot import get_driver, on_command
from nonebot.params import CommandArg
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
    GroupMessageEvent,
    Message,
)

from .models import cmd_search_config_parser, cmd_search_parser
from .services.managers import group_cfg, command_manager
from .plugins import handle_search

__translation_table = str.maketrans({
    '；': ';',
    '：': ':',
    '，': ',',
    '（': '(',
    '）': ')',
    '【': '[',
    '】': ']',
    '《': '<',
    '》': '>',
    '？': '?',
    '！': '!',
    '。': '.',
    '、': ',',
})

driver = get_driver()
superusers = driver.config.superusers

cmd_search = on_command("搜图")
cmd_search_config = on_command("搜图配置")

def authenticate(event: MessageEvent) -> bool:
    """验证用户是否为超级管理员或群管理员"""
    if isinstance(event, GroupMessageEvent):
        logger.info(f"验证用户 {event.user_id} 是否为 {event.group_id} 管理员")
    return ((str(event.user_id) in superusers) or
            (isinstance(event, GroupMessageEvent) and event.sender.role in ["owner", "admin"]))


def is_image(reply):
    """检查消息段是否为图片类型"""
    referenced_msg = reply
    for segment in referenced_msg.message:
        # 判断该 segment 是否为图片类型
        logger.info(f"消息段类型: {segment.type}")
        if isinstance(segment, MessageSegment) and segment.type == 'image':
            return segment
    return False


def raw_cmd_handler(text_raw: str, is_image_flag: bool = False, method: str = 'search'):
    text = text_raw.translate(__translation_table)
    argv = shlex.split(text)

    # 如果没有输入任何内容，直接返回帮助信息
    if not text:
        argv = ['--help']
    if is_image_flag and not text:
        argv = ['0.25']

    if method == 'search':
        return cmd_search_parser.parse_args(argv)
    else:
        return cmd_search_config_parser.parse_args(argv)


@cmd_search.handle()
async def search(
    bot: Bot,
    event: Union[MessageEvent, PrivateMessageEvent, GroupMessageEvent], 
    arg: Message = CommandArg()
):
    if not isinstance(event, GroupMessageEvent):
        await cmd_search.finish("搜图仅限群聊使用。")

    image_segment = None
    if event.reply:
        image_segment = is_image(event.reply)

    text_raw = arg.extract_plain_text().strip()
    try:
        opts = raw_cmd_handler(text_raw, is_image_flag=bool(image_segment))
        logger.info(opts)
    except SystemExit:
        # 获取帮助信息或错误信息
        output_message = cmd_search_parser.get_output()
        await cmd_search.finish(output_message)
    except Exception as e:
        await cmd_search.finish(f"参数解析出错：{e}")

    if opts.status:
        result = await command_manager.handle_status(event)
        await cmd_search.finish(result)

    if not command_manager.check_feature_enabled(event):
        await cmd_search.finish("搜图未在本群开启，管理员请用 .搜图配置 --on 启动")

    if opts.tags:
        result = command_manager.get_tags_info(event)
        await cmd_search.send(result)

    search_query = {}

    if event.reply:
        if image_segment:
            search_query['mode'] = 'img2img'
            image_url = image_segment.data.get('url')
            if image_url is not None:
                search_query["url"] = image_url
            if opts.params:
                search_query["distance"] = opts.params
        else:
            await cmd_search.finish("回复的消息中不包含图片。")
    else:
        search_query['mode'] = 'tags2img'
        search_query["tags"] = opts.params

    await handle_search(
        cmd_search, 
        event=event, 
        onglobal=group_cfg.get_onglobal(str(event.group_id)), 
        bot=bot,
        search_query=search_query
    )


@cmd_search_config.handle()
async def search_config(
    bot: Bot,
    event: Union[MessageEvent, PrivateMessageEvent, GroupMessageEvent], 
    arg: Message = CommandArg()
):
    if not authenticate(event):
        await cmd_search_config.finish("只有群聊管理员和超级管理员可以配置搜图功能")

    if not isinstance(event, GroupMessageEvent):
        await cmd_search_config.finish("搜图仅限群聊使用。")

    text_raw = arg.extract_plain_text().strip()
    # 输入为纯参数或者tags加参数
    try:
        opts = raw_cmd_handler(text_raw, method='config')
        logger.info(opts)
    except SystemExit:
        # 获取帮助信息或错误信息
        output_message = cmd_search_config_parser.get_output()
        await cmd_search_config.finish(output_message)
    except Exception as e:
        await cmd_search_config.finish(f"参数解析出错：{e}")

    # 处理开启/关闭
    result = await command_manager.handle_enable_disable(event, opts)
    if result:
        await cmd_search_config.send(result)

    # 处理全局标签
    result, need_confirm = await command_manager.handle_global_tags(event, opts, cmd_search_config)
    if result:
        await cmd_search_config.send(result)
        if need_confirm:
            return

    # 处理标签修改
    result = await command_manager.handle_tags_modification(event, opts)
    if result:
        await cmd_search_config.send(result)