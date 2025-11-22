from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    Bot,
)


class Sender:
    def __init__(self, bot: Bot, user_id: int, group_id: int):
        self.bot = bot
        self.at_user = MessageSegment.at(user_id)
        self.group_id = group_id
        self._msg_content: MessageSegment
        self._msg_info: str = ""

    @property
    def msg(self) -> Message:
        return self._msg_content + MessageSegment.text(self._msg_info)

    @msg.setter
    def msg(self, info: dict[str, int | str]) -> None:
        self._msg_info = f"id: {info['id']}\nscore: {info['score']}"
        url = str(info['url'])
        file_type = url.split('.')[-1].lower() if '.' in url else ''
        if file_type in ['webm', 'mp4']:
            self._msg_content = MessageSegment.video(url)
        else:
            self._msg_content = MessageSegment.image(url)

    def send(self):
        return self.bot.send_group_msg(
            group_id=self.group_id,
            message=self.at_user + self.msg
        )


class CommonSender(Sender):
    def __init__(self, bot: Bot, user_id: int, group_id: int):
        super().__init__(bot, user_id, group_id)

    @property
    def msg(self) -> Message:
        """重写以支持带标签的消息"""
        return super().msg
        
    @msg.setter
    def msg(self, value: tuple[dict[str, int | str], str, str]) -> None:
        """支持两种赋值方式: 仅信息字典 或 (信息字典, 标签) 元组"""
        info, tags, additional_msg = value
        Sender.msg.fset(self, info)  # type: ignore
        self._msg_info += f"\ntags: {tags}"
        if additional_msg:
            self._msg_info += f"\n提示：{additional_msg}"


class MergeForwardSender(CommonSender):
    def __init__(self, bot: Bot, user_id: int, group_id: int):
        super().__init__(bot, user_id, group_id)

    def send(self):
        nodes = [
            {
                "type": "node",
                "data": {
                    "name": "phimg",
                    "uin": str(self.bot.self_id),
                    "content": self._msg_content
                }
            },
            {
                "type": "node",
                "data": {
                    "name": "phimg",
                    "uin": str(self.bot.self_id),
                    "content": self._msg_info
                }
            }
        ]
        return self.bot.send_group_forward_msg(
            group_id=self.group_id,
            messages=nodes
        )


class MultiSegmentSender(Sender):
    def __init__(self, bot: Bot, user_id: int, group_id: int):
        super().__init__(bot, user_id, group_id)
        self.msg_list = [Message()]
        self.distance = 0.25

    def add_messages(self, messages: list[dict[str, int | str]], distance: float) -> None:
        """添加多条消息"""
        for info in messages:
            temp_sender = Sender(self.bot, 0, self.group_id)
            temp_sender.msg = info
            self.msg_list.append(temp_sender.msg)
        self.distance = distance
    
    def send(self):
        """发送包含多个消息段的消息"""
        combined_msg = Message()
        for msg in self.msg_list:
            combined_msg += msg
        return self.bot.send_group_msg(
            group_id=self.group_id,
            message=self.at_user + f"\ndistance: {self.distance}" + combined_msg
        )