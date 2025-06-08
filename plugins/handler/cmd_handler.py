from typing import Union
import shlex
import sys
from io import StringIO

from nonebot import get_driver, on_command
from nonebot.params import CommandArg
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
    Message,
)

from ...models import cmd_parser
from ...utils import group_cfg
from ..search import search

driver = get_driver()
driver.config.command_start = {".", "。"}

cmd = on_command("搜图")

@cmd.handle()
async def _(
    event: Union[MessageEvent, PrivateMessageEvent, GroupMessageEvent], 
    arg: Message = CommandArg()
):
    if not isinstance(event, GroupMessageEvent):
        await cmd.finish("该命令仅限群聊使用，请在群聊中使用。")

    if not group_cfg.get_status(str(event.group_id)):
        await cmd.finish("功能未在本群开启，管理员请用 。搜图 --on 启动")

    text = arg.extract_plain_text().strip()
    argv = shlex.split(text)
    
    index = -1
    for _ in argv:
        if _.startswith("--"):
            index = argv.index(_)
            break
    if index == -1:
        index = len(argv)
    tags_str = ''.join(argv[:index])

    # 输入为纯参数或者tags加参数
    if not index or index and index < len(argv):
        try:
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
        
            opts = cmd_parser.parse_args(argv[index:])
            sys.stdout = old_stdout
        except SystemExit:
            sys.stdout = old_stdout
            help_message = captured_output.getvalue()
            await cmd.finish(help_message)
        except Exception as e:
            sys.stdout = old_stdout
            await cmd.finish(f"参数解析出错：{e}")

        if opts.tags and not tags_str:
            group_tags = group_cfg.get_tags(str(event.group_id))
            group_tags = group_tags if group_tags else "当前群聊没有内置标签"
            await cmd.finish(f"当前群聊内置标签：{', '.join(group_tags)}")
            
        if opts.on and opts.off:
            pass
        elif opts.on:
            pass
        elif opts.off:
            pass

        if opts.add:
            pass
        if opts.rm:
            pass

    if tags_str:
        await search(cmd, event=event, tags_str=tags_str)