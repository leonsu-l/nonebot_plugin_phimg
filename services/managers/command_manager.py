from typing import Optional, TYPE_CHECKING
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.log import logger

class CommandManager:
    """群聊指令管理器"""
    
    def __init__(self, group_config_manager):
        """初始化命令管理器"""
        self.group_cfg = group_config_manager
    
    async def handle_status(self, event: GroupMessageEvent) -> str:
        """处理状态查询"""
        try:
            status = self.group_cfg.get_info(str(event.group_id))
            return (f"当前群聊搜图功能状态：\n"
                   f" 启用：{status.enabled}\n"
                   f" 标签：{', '.join(status.tags)}\n"
                   f" 全局标签：{'启用' if status.onglobal else '禁用'}")
        except ValueError:
            return "未找到群聊配置，请联系管理员"
    
    async def handle_enable_disable(self, event: GroupMessageEvent, opts) -> Optional[str]:
        """处理开启/关闭功能"""
        if opts.on and opts.off:
            return "不能同时开启和关闭搜图功能，请选择一个操作"
        
        if opts.on:
            await self.group_cfg.enable(str(event.group_id))
            return "搜图功能已在本群开启"
        elif opts.off:
            await self.group_cfg.disable(str(event.group_id))
            return "搜图功能已在本群关闭"
        
        return None
    
    async def handle_global_tags(self, event: GroupMessageEvent, opts, cmd) -> tuple[Optional[str], bool]:
        """
        处理全局标签设置
        返回: (消息内容, 是否需要等待确认)
        """
        if opts.onglobal and opts.offglobal:
            return "不能同时开启和关闭全局标签，请选择一个操作", False
        
        if opts.onglobal:
            await self.group_cfg.set_onglobal(str(event.group_id))
            return "全局标签已启用", False
        elif opts.offglobal:
            if not hasattr(cmd, 'confirm_offglobal'):
                cmd.confirm_offglobal = True
                return "关闭全局标签，机器人将会搜出非safe图片\n请自行承担可能的炸群风险\n再输入一遍指令确认关闭", True
            await self.group_cfg.set_offglobal(str(event.group_id))
            del cmd.confirm_offglobal
            return "全局标签已禁用", False
        
        return None, False
    
    async def handle_tags_modification(self, event: GroupMessageEvent, opts) -> Optional[str]:
        """处理标签添加/删除"""
        add_msg = rm_msg = ""
        
        if opts.add:
            await self.group_cfg.add_tags(str(event.group_id), self._parse_tags(opts.add))
            add_msg = f"添加成功，本群标签现为: {self._get_current_tags(str(event.group_id))}"
        
        if opts.rm:
            await self.group_cfg.remove_tags(str(event.group_id), self._parse_tags(opts.rm))
            rm_msg = f"删除成功，本群标签现为: {self._get_current_tags(str(event.group_id))}"
        
        if opts.add and opts.rm:
            return f"修改成功，本群标签现为: {self._get_current_tags(str(event.group_id))}"
        elif opts.add or opts.rm:
            return rm_msg or add_msg
        
        return None
    
    def check_feature_enabled(self, event: GroupMessageEvent) -> bool:
        """检查功能是否启用"""
        return self.group_cfg.get_status(str(event.group_id))
    
    def get_tags_info(self, event: GroupMessageEvent) -> str:
        """获取标签信息"""
        group_tags = self._get_current_tags(str(event.group_id))
        return f"当前群聊内置标签：{group_tags}"
    
    def _parse_tags(self, tags_raw: str) -> list[str]:
        """解析标签字符串为标签列表"""
        if not tags_raw:
            return []
        tags_str = ' '.join(tags_raw).strip()
        return [tag.strip() for tag in tags_str.split(",") if tag.strip()]
    
    def _get_current_tags(self, group_id: str) -> str:
        """获取标签列表"""
        group_tags = self.group_cfg.get_tags(str(group_id))
        group_tags = group_tags or ["无"]
        return ', '.join(group_tags)