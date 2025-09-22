from typing import Union
import shlex

from nonebot import get_driver, on_command
from nonebot.params import CommandArg
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
    Message,
)

from .models import cmd_parser
from .plugins import search
from .services.managers import group_cfg, command_manager

translation_table = str.maketrans({
    '；': ';',           # 将 ； 替换为 ;
    '：': ':',           # 将 ： 替换为 :
    '，': ',',          # 将 ，替换为 ,
    '（': '(',          # 将 （ 替换为 (
    '）': ')',          # 将 ） 替换为 )
    '【': '[',          # 将 【 替换为 [
    '】': ']',          # 将 】 替换为 ]
    '《': '<',          # 将 《 替换为 <
    '》': '>',          # 将 》 替换为 >
    '？': '?',          # 将 中文问号 替换为 英文问号
    '！': '!',          # 将 中文感叹号 替换为 英文感叹号
    '。': '.',          # 将 中文句号 替换为 英文句号
    '、': ',',          # 将 中文顿号 替换为 英文逗号
})

driver = get_driver()

superusers = driver.config.superusers

cmd = on_command("搜图")

@cmd.handle()
async def _(
    bot: Bot,
    event: Union[MessageEvent, PrivateMessageEvent, GroupMessageEvent], 
    arg: Message = CommandArg()
):
    if not isinstance(event, GroupMessageEvent):
        await cmd.finish("搜图仅限群聊使用。")

    text_raw = arg.extract_plain_text().strip()
    text = text_raw.translate(translation_table)
    argv = shlex.split(text)
    
    # 如果没有输入任何内容，直接返回帮助信息
    if not text:
        cmd_parser.print_help()
        output_message = cmd_parser.get_output()
        await cmd.finish(output_message)

    # 初处理
    index = -1
    for _ in argv:
        if _.startswith("--"):
            index = argv.index(_)
            break
    if index == -1:
        index = len(argv)
    tags_str = ' '.join(argv[:index])

    # 输入为纯参数或者tags加参数
    try:
        opts = cmd_parser.parse_args(argv[index:])
        logger.info(opts)
    except SystemExit:
        # 获取帮助信息或错误信息
        output_message = cmd_parser.get_output()
        await cmd.finish(output_message)
    except Exception as e:
        await cmd.finish(f"参数解析出错：{e}")

    if opts.status:
        result = await command_manager.handle_status(event)
        await cmd.finish(result)

    if opts.on or opts.off or opts.add or opts.rm or opts.onglobal or opts.offglobal:
        if not authenticate(event):
            await cmd.finish("只有群聊管理员和超级管理员可以设置搜图功能")

        # 处理开启/关闭
        result = await command_manager.handle_enable_disable(event, opts)
        if result:
            await cmd.send(result)

        # 处理全局标签
        result, need_confirm = await command_manager.handle_global_tags(event, opts, cmd)
        if result:
            await cmd.send(result)
            if need_confirm:
                return

        # 处理标签修改
        result = await command_manager.handle_tags_modification(event, opts)
        if result:
            await cmd.send(result)

        if not tags_str:
            return

    if not command_manager.check_feature_enabled(event):
        await cmd.finish("搜图未在本群开启，管理员请用 .搜图 --on 启动")

    if opts.tags:
        result = command_manager.get_tags_info(event)
        await cmd.send(result)

    # query = {
    #     tags_str
    # }

    if tags_str:
        await search(
            cmd, 
            event=event, 
            tags_str=tags_str, 
            onglobal=group_cfg.get_onglobal(str(event.group_id)), 
            bot=bot
        )

def authenticate(event: MessageEvent) -> bool:
    """验证用户是否为超级管理员或群管理员"""
    if isinstance(event, GroupMessageEvent):
        logger.info(f"Authenticating user {event.user_id} in group {event.group_id}")
    return ((str(event.user_id) in superusers) or
            (isinstance(event, GroupMessageEvent) and event.sender.role in ["owner", "admin"]))