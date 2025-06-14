from typing import Union
import shlex

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
from ...utils import group_cfg, init
from ..search import search

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
driver.config.command_start = {".", "。"}

cmd = on_command("搜图")

@cmd.handle()
async def _(
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
    tags_str = ''.join(argv[:index])

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
     
    if event.user_id == SUPERUSER or event.sender.role in ["owner", "admin"]:
        if opts.on and opts.off:
            await cmd.finish("不能同时开启和关闭搜图功能，请选择一个操作")
        if opts.on:
            await group_cfg.enable(str(event.group_id))
            await cmd.send("搜图功能已在本群开启")
        elif opts.off:
            await group_cfg.disable(str(event.group_id))
            await cmd.send("搜图功能已在本群关闭")

        if opts.onglobal and opts.offglobal:
            await cmd.finish("不能同时开启和关闭全局标签，请选择一个操作")
        if opts.onglobal:
            await group_cfg.set_onglobal(str(event.group_id))
            await cmd.send("全局标签已启用")
        elif opts.offglobal:
            await group_cfg.set_offglobal(str(event.group_id))
            await cmd.send("全局标签已禁用")

        add_msg = rm_msg = ""
        if opts.add:
            await group_cfg.add_tags(str(event.group_id), parse_tags(opts.add))
            add_msg = f"添加成功，本群标签现为: {get_current_tags(str(event.group_id))}"
        if opts.rm:
            await group_cfg.remove_tags(str(event.group_id), parse_tags(opts.rm))
            rm_msg = f"删除成功，本群标签现为: {get_current_tags(str(event.group_id))}"
        if opts.add and opts.rm:
            await cmd.send(f"修改成功，本群标签现为: {get_current_tags(str(event.group_id))}")
        elif opts.add or opts.rm:
            await cmd.send(rm_msg or add_msg)
    
    elif opts.on or opts.off or opts.add or opts.rm:
        await cmd.finish("只有群聊管理员和超级管理员可以设置搜图功能")


    if not group_cfg.get_status(str(event.group_id)):
        await cmd.finish("搜图未在本群开启，管理员请用 .搜图 --on 启动")

    if opts.tags:
        group_tags = get_current_tags(str(event.group_id))
        await cmd.send(f"当前群聊内置标签：{group_tags}")
    
    if opts.status:
        try:
            status = group_cfg.get_info(str(event.group_id))
            await cmd.finish(f"当前群聊搜图功能状态：\n 启用：{status.enabled}\n 标签：{', '.join(status.tags)}\n 全局标签：{'启用' if status.onglobal else '禁用'}")
        except ValueError:
            await cmd.finish("未找到群聊配置，请联系管理员")

    # query = {
    #     tags_str
    # }

    if tags_str:
        await search(cmd, event=event, tags_str=tags_str, onglobal=group_cfg.get_onglobal(str(event.group_id)))

def parse_tags(tags_raw: str) -> list[str]:
    """解析标签字符串为标签列表"""
    if not tags_raw:
        return []
    tags_str = ' '.join(tags_raw).strip()
    return [tag.strip() for tag in tags_str.split(",") if tag.strip()]

def get_current_tags(group_id: str) -> str:
    """获取标签列表"""
    group_tags = group_cfg.get_tags(str(group_id))
    group_tags = group_tags or ["无"]
    return ', '.join(group_tags)
