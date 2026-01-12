from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    Bot,
)
from dataclasses import dataclass
from typing import Optional

@dataclass
class MessageInfo:
    """消息信息数据类"""
    id: int | str
    score: int | str
    url: str
    tags: Optional[str] = None
    additional_msg: Optional[str] = None
    

class Sender:
    def __init__(self, bot: Bot, user_id: int, group_id: int):
        self.bot = bot
        self.at_user = MessageSegment.at(user_id)
        self.group_id = group_id
        self._msg_content: MessageSegment = MessageSegment.image("")
        self._msg_info: str = ""

    def _get_file_type(self, url: str) -> str:
        """提取文件类型"""
        return url.split('.')[-1].lower() if '.' in url else ''

    def _format_base_info(self, info: MessageInfo) -> str:
        """格式化基础信息"""
        return f"id: {info.id}\nscore: {info.score}"

    def _set_media_content(self, url: str) -> None:
        """根据URL设置媒体内容"""
        file_type = self._get_file_type(url)
        if file_type in ['webm', 'mp4']:
            self._msg_content = MessageSegment.video(url)
        else:
            self._msg_content = MessageSegment.image(url)

    @property
    def msg(self) -> Message:
        return self._msg_content + MessageSegment.text(self._msg_info)

    @msg.setter
    def msg(self, info: MessageInfo) -> None:
        self._msg_info = self._format_base_info(info)
        self._set_media_content(info.url)

    def send(self):
        return self.bot.send_group_msg(
            group_id=self.group_id,
            message=self.at_user + self.msg
        )


class CommonSender(Sender):
    """支持标签和附加消息的发送器"""

    @Sender.msg.setter
    def msg(self, info: MessageInfo) -> None:
        """设置带标签的消息"""
        super(CommonSender, self.__class__).msg.fset(self, info)  # type: ignore
        if info.tags:
            self._msg_info += f"\ntags: {info.tags}"
        if info.additional_msg:
            self._msg_info += f"\n提示：{info.additional_msg}"


class MergeForwardSender(CommonSender):
    """合并转发消息发送器"""

    def _build_node(self, content: str | MessageSegment) -> dict:
        """构建转发节点"""
        return {
            "type": "node",
            "data": {
                "name": "phimg",
                "uin": str(self.bot.self_id),
                "content": content
            }
        }
    
    def send(self):
        nodes = [
            self._build_node(self._msg_content),
            self._build_node(self._msg_info)
        ]
        return self.bot.send_group_forward_msg(
            group_id=self.group_id,
            messages=nodes
        )


class MultiSegmentSender(Sender):
    """多消息段发送器"""

    def __init__(self, bot: Bot, user_id: int, group_id: int):
        super().__init__(bot, user_id, group_id)
        self.msg_list: list[Message] = []
        self.distance = 0.25

    def add_messages(self, messages: list[MessageInfo], distance: float) -> None:
        """添加多条消息"""
        for info in messages:
            msg_content = self._build_message(info)
            self.msg_list.append(msg_content)
        self.distance = distance
    
    def _build_message(self, info: MessageInfo) -> Message:
        """构建单条消息"""
        self._set_media_content(info.url)
        msg_text = self._format_base_info(info)
        return self._msg_content + MessageSegment.text(msg_text)

    def send(self):
        """发送包含多个消息段的消息"""
        combined_msg = Message()
        for msg in self.msg_list:
            combined_msg += msg
        return self.bot.send_group_msg(
            group_id=self.group_id,
            message=self.at_user + f"\ndistance: {self.distance}" + combined_msg
        )