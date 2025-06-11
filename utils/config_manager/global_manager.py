import json
import aiofiles
from pathlib import Path

from src.plugins.nonebot_plugin_dbimg.models import GlobalConfig

class GlobalConfigManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None

    async def init(self):
        """异步初始化，加载配置"""
        self.data = await self.load()

    async def load(self) -> GlobalConfig:
        """从 JSON 文件加载配置，如果文件不存在则返回一个空的 Data 对象"""
        if Path(self.file_path).exists():
            async with aiofiles.open(self.file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                loaded_data = json.loads(content)
            return GlobalConfig.parse_obj(loaded_data)
        else:
            return GlobalConfig()

    async def save(self):
        """将当前的配置保存到 JSON 文件"""
        async with aiofiles.open(self.file_path, "w", encoding="utf-8") as f:
            content = json.dumps(self.data.dict(), ensure_ascii=False, indent=2)
            await f.write(content)

    def get_tags(self) -> list[str]:
        """获取全局 tags"""
        tags = self.data.tags
        return tags if tags else []
    
    def get_status(self) -> bool:
        """获取全局状态"""
        enabled = self.data.enabled
        return enabled if enabled else True

    def update_tags(self, new_tags: list[str]):
        """更新全局配置中的 tags"""
        pass
    
    def add_tags(self, tags: list[str]):
        """向全局配置中添加新的 tags"""
        pass

    def rm_tags(self, tags: list[str]):
        """从全局配置中删除指定的 tags"""
        pass