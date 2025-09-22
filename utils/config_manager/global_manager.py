import json
import aiofiles
from pathlib import Path

from ...models import GlobalConfig

class GlobalConfigManager:
    def __init__(self):
        self.data = GlobalConfig()

    def get_tags(self) -> list[str]:
        """获取全局 tags"""
        tags = self.data.tags
        return tags if tags else []
    
    def get_status(self) -> bool:
        """获取全局状态"""
        enabled = self.data.enabled
        return enabled if enabled else True
    
    def get_key(self) -> str:
        """获取全局 API Key"""
        key = self.data.key
        return key if key else ""