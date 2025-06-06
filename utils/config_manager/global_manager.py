import json
from pathlib import Path

from src.plugins.nonebot_plugin_dbimg.models import GlobalConfig

class GlobalConfigManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self.load()

    def load(self) -> GlobalConfig:
        """从 JSON 文件加载配置，如果文件不存在则返回一个空的 Data 对象"""
        if Path(self.file_path).exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            return GlobalConfig.parse_obj(loaded_data)
        else:
            return GlobalConfig()

    def save(self):
        """将当前的配置保存到 JSON 文件"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data.dict(), f, ensure_ascii=False, indent=2)
